import re
import pandas as pd
from typing import List, Dict
from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.config.elasticsearch_client import es_connect
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.base_rule import BaseRule

class Rule(BaseRule):
    def __init__(self, rule_params: RuleParams, l_s: str, d_c: str, fields: List[Field]):
        super().__init__(rule_params, l_s, d_c, fields)
        self.field_value_field = self._get_field_value_field()

    def _get_field_value_field(self):
        for field in self.filter1_params['fields']:
            if field.field_value_flag:
                return field
        return None

    def _filter_query_formatter(self):
        try:
            rule_params = self.rule_params
            query = {
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"COUNTRY": rule_params.category_code}},
                            {"terms": {"C_OR_D": [f"{self.filter1_params['l_s']} {self.filter1_params['d_c']}R"]}}
                        ]
                    }
                }
            }

            if rule_params.set_id != 'ALL':
                query["query"]["bool"]["filter"].append({"terms": {"LOCAL_ACC_NO": rule_params.set_id}})

            if self.field_value_field:
                query["query"]["bool"]["filter"].append({
                    "regexp": {self.field_value_field.name: self.field_value_field.field_value_params['field_value']['exp']}
                })

            return {
                'track_total_hits': True,
                **query,
                "_source": selected_fields
            }
        except Exception as e:
            raise ValueError(f"Failed to format query for the field value rule: {e}")

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

    def _find_matching_transaction(self, es, transaction):
        field_name = self.field_value_field.field_value_params['field_value']['field_name']
        exp = self.field_value_field.field_value_params['field_value']['exp']
        match = re.search(exp, transaction[field_name])
        
        if not match:
            return None

        extracted_value = match.group()
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"RELATIONSHIP_ID": transaction['RELATIONSHIP_ID']}},
                        {"term": {"ITEM_ID": extracted_value}},
                        {"bool": {"must_not": {"term": {"ITEM_ID": transaction['ITEM_ID']}}}}
                    ]
                }
            }
        }

        response = es.search(index=matched_data_index, body=query, size=1)
        hits = response['hits']['hits']
        return hits[0]['_source'] if hits else None

    def find_matches(self) -> pd.DataFrame:
        query = self._filter_query_formatter()
        scroll_id = None
        matched_transactions = []
        es = es_connect()

        while True:
            scroll_id, transactions = self._scroll_transactions(query, scroll_id)
            if not transactions:
                break

            for transaction in transactions:
                matching_transaction = self._find_matching_transaction(es, transaction)
                if matching_transaction:
                    matched_transactions.extend([transaction, matching_transaction])

        if matched_transactions:
            final_df = pd.DataFrame(matched_transactions)
            if self.rule_params.amount:
                final_df = final_df.groupby('RELATIONSHIP_ID').filter(
                    lambda group: self.check_amount_flag_condition('AMOUNT', self.rule_params.amount, group)
                )
            final_df['Rule_Id'] = self.rule_params.unique_rule_id
            return final_df

        return pd.DataFrame()
