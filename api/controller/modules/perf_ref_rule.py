import re
import pandas as pd
from typing import List, Dict
from collections import defaultdict
from difflib import SequenceMatcher

from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.config.elasticsearch_client import es_connect
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.base_rule import BaseRule

class Rule(BaseRule):
    def __init__(self, rule_params: RuleParams, l_s: str, d_c: str, fields: List[Field]):
        super().__init__(rule_params, l_s, d_c, fields)

    def _process_fields(self, fields, filter_key):
        for field in fields:
            if field.perf_ref_flag:
                field_id = field.id if field.id else 'none'
                if field_id not in self.filter_mapping:
                    self.filter_mapping[field_id] = {
                        'filter1_fields': [],
                        'filter2_fields': [],
                        'params': field.perf_ref_params
                    }
                self.filter_mapping[field_id][f'{filter_key}_fields'].append(field.name)

    def validate_rule(self):
        self._process_fields(self.filter1_params['fields'], 'filter1')
        self._process_fields(self.filter2_params['fields'], 'filter2')

        if not self.filter_mapping:
            raise ValueError("No PerfRef fields found in either filter")

        for field_info in self.filter_mapping.values():
            if not field_info['filter1_fields'] or not field_info['filter2_fields']:
                raise ValueError("PerfRef fields must be present in both filters")

        return True

    def _find_top_5_common_substrings(self, strings, params):
        if not strings:
            return []

        common_substrings = set(self._get_substrings(strings[0], params))
        for s in strings[1:]:
            common_substrings &= set(self._get_substrings(s, params))

        return sorted(list(common_substrings), key=len, reverse=True)[:5]

    def _get_substrings(self, s, params):
        min_len = params.get('min_length', 5)
        max_len = params.get('max_length', 15)
        exact_len = params.get('exact_length')

        if exact_len:
            return [s[i:i+exact_len] for i in range(len(s)-exact_len+1) if '|' not in s[i:i+exact_len]]
        else:
            return [s[i:j] for i in range(len(s)) for j in range(i + min_len, min(i + max_len + 1, len(s) + 1)) if '|' not in s[i:j]]

    def _preprocess_string(self, s: str):
        return re.sub(r'[^\w\s]', '', s.strip())

    def _process_relationship_group(self, relationship_group):
        def get_tran_type(filter_params):
            if filter_params['d_c'] != 'A':
                return [f"{filter_params['l_s']} {filter_params['d_c']}R"]
            else:
                return [f"{filter_params['l_s']} CR", f"{filter_params['l_s']} DR"]

        filter1_tran_type = get_tran_type(self.filter1_params)
        filter2_tran_type = get_tran_type(self.filter2_params)

        matches = {}

        for field_id, field_info in self.filter_mapping.items():
            filter1_values = ['|'.join(self._preprocess_string(transaction.get(field, '')) 
                            for field in field_info['filter1_fields'])
                            for transaction in relationship_group 
                            if transaction['C_OR_D'] in filter1_tran_type]
            
            filter2_values = ['|'.join(self._preprocess_string(transaction.get(field, '')) 
                            for field in field_info['filter2_fields'])
                            for transaction in relationship_group 
                            if transaction['C_OR_D'] in filter2_tran_type]

            common_substrings = self._find_top_5_common_substrings([filter1_values + filter2_values], field_info['params'])

            if common_substrings:
                matches[field_id] = common_substrings

        return matches

    def _group_by_trans_by_rel(self, transactions):
        grouped_transactions = defaultdict(list)
        for txn in transactions:
            relationship_id = txn['RELATIONSHIP_ID']
            grouped_transactions[relationship_id].append(txn)
        return grouped_transactions

    def _scroll_transactions(self, query, scroll_id):
        try:
            es = es_connect()
            if scroll_id:
                response = es.scroll(scroll_id=scroll_id, scroll='1m')
            else:
                response = es.search(index=matched_data_index, body=query, scroll='1m', size=10000)

            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            transactions = [hit['_source'] for hit in hits]
            return scroll_id, transactions
        except Exception as e:
            raise ValueError(f'Failed to get matches for the filter: {e}')

    def find_matches(self) -> pd.DataFrame:
        query = self._filter_query_formatter()
        scroll_id = None
        matched_transactions = []

        while True:
            scroll_id, transactions = self._scroll_transactions(query, scroll_id)
            if not transactions:
                break

            grouped_transactions = self._group_by_trans_by_rel(transactions)

            for relationship_id, relationship_group in grouped_transactions.items():
                matches = self._process_relationship_group(relationship_group)
                if matches:
                    for transaction in relationship_group:
                        transaction['MATCHED_VALUE'] = ', '.join([
                            f"{field_id}: {', '.join(common_substrings)}"
                            for field_id, common_substrings in matches.items()
                        ])
                    matched_transactions.extend(relationship_group)

        if matched_transactions:
            final_df = pd.DataFrame(matched_transactions)
            if self.rule_params.amount:
                final_df = final_df.groupby('RELATIONSHIP_ID').filter(
                    lambda group: self.check_amount_flag_condition('AMOUNT', self.rule_params.amount, group)
                )
            final_df['Rule_Id'] = self.rule_params.unique_rule_id
            return final_df

        return pd.DataFrame()

    def _filter_query_formatter(self):
        try:
            print('---')
            print(f'Formatting query for PerfRef rule')
            rule_params = self.rule_params
            query = {
                "query": {
                    "bool": {
                        "filter": []
                    }
                }
            }
            conditions = {
                "bool": {
                    "must": [
                        {"term": {
                            "COUNTRY": rule_params.category_code
                        }}
                    ],
                    "should": [],
                    "minimum_should_match": 1
                }
            }

            set_ids = rule_params.set_id
            if set_ids != 'ALL':
                condition = {"terms": {"LOCAL_ACC_NO": set_ids}}
                conditions["bool"]["must"].append(condition)

            tran_type = [f"{self.filter1_params['l_s']} CR", f"{self.filter1_params['l_s']} DR"]
            print(f'Trans Type: {tran_type}')
            condition = {"terms": {"C_OR_D": tran_type}}
            conditions["bool"]["must"].append(condition)

            query["query"]["bool"]["filter"].append(conditions)

            q = {
                'track_total_hits': True,
                **query,
                "_source": selected_fields
            }

            print(f'PerfRef query: {q}')
            return q
        except Exception as e:
            raise ValueError(f"Failed to format query for the PerfRef rule: {e}")
