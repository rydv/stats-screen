import re
import pandas as pd
from typing import List
from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.config.elasticsearch_client import es_connect
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.base_rule import BaseRule

class Rule(BaseRule):
    def __init__(self, rule_params: RuleParams, l_s: str, d_c: str, fields: List[Field]):
        super().__init__(rule_params, l_s, d_c, fields)

    def _filter_query_formatter(self, filter_params, filter_id):
        try:
            rule_params = self.rule_params
            query = {
                "query": {
                    "bool": {
                        "filter": [
                            # {
                            #     "range": {
                            #         "LAST_ACTION_DATE": {
                            #             "format": "strict_date_optional_time",
                            #             "gte": str(from_date) + "T00:00:00Z",
                            #             "lte": str(to_date) + "T23:59:59Z"
                            #         }
                            #     }
                            # }
                        ]
                    }
                }
            }
            conditions = {
                "bool": {
                    "must": [
                        {"term": {
                            # "AGENT_CODE": rule_params.agent_code,
                            "COUNTRY": rule_params.category_code
                        }}
                    ],
                    "should": [],
                    "minimum_should_match": 1
                }
            }
            
            #speicfic set ids check
            set_ids = rule_params.set_id
            if set_ids != 'ALL':
                condition = {"terms": {"LOCAL_ACC_NO": set_ids}}
                conditions["bool"]["must"].append(condition)

            if filter_params['d_c'] != 'A':
                tran_type = [f"{filter_params['l_s']} {filter_params['d_c']}R"]
            else:
                tran_type = [f"{filter_params['l_s']} CR", f"{filter_params['l_s']} DR"]
            
            print(f'Trans Type: {tran_type}')
            condition = {"terms": {"C_OR_D": tran_type}}
            conditions["bool"]["must"].append(condition)

            # print(f'Filter-{filter_id} values:')
            for field in filter_params['fields']:
                condition = self._create_field_condition(field)
                if condition:
                    conditions["bool"]["should"].append(condition)

            query["query"]["bool"]["filter"].append(conditions)

            q={
                'track_total_hits': True,
                **query,
                "_source": selected_fields
            }
            return q
        except Exception as e:
            raise ValueError(f"Failed to format query for the rule: {e}")

    def _get_filter_matches(self, query):
        try:
            scroll_id = None
            es = es_connect()
            res = es.search(index=matched_data_index, body=query, scroll='2m', size=1000)
            scroll_id = res['_scroll_id']
            hits = res['hits']['hits']
            all_hits = hits

            while len(hits) > 0:
                response = es.scroll(scroll_id=scroll_id, scroll='2m')
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
                all_hits.extend(hits)

            df = pd.DataFrame([hit['_source'] for hit in all_hits])
            return df

        except Exception as e:
            raise ValueError(f'Failed to get matches for the filter: {e}')
        finally:
            if scroll_id:
                es.clear_scroll(scroll_id=scroll_id)

    def _extract_matched_value(self, row, filter_field_values):
        matched_values = []
        partname_values = []
        for field in filter_field_values:
            if field.exp_flag or field.partname_flag:
                match = re.search(field.search_agg_exp, row[field.name])
                if match:
                    groups = match.groups()
                    matched_values.extend(groups[:-1])  # All groups except the last one (partname)
                    partname_values.append(groups[-1])  # Last group is partname
        
        return " | ".join(matched_values), " ".join(partname_values)

    def _compare_partnames(self, name1, name2):
        name1_parts = set(name1.lower().split())
        name2_parts = set(name2.lower().split())
        return bool(name1_parts & name2_parts)

    def find_matches(self):
        queries = {
            "filter1": self._filter_query_formatter(self.filter1_params, 1),
            "filter2": self._filter_query_formatter(self.filter2_params, 2),
        }

        filter1_matches = self._get_filter_matches(queries['filter1'])
        filter2_matches = self._get_filter_matches(queries['filter2'])

        print(f'# filter-1 matches: {len(filter1_matches)}')
        print(f'# filter-2 matches: {len(filter2_matches)}')

        if not (len(filter1_matches) and len(filter2_matches)):
            print('Matches not found for at least one of the filters')
            return pd.DataFrame(columns=selected_fields)

        filter1_matches['Filter'] = 'Filter-1'
        filter2_matches['Filter'] = 'Filter-2'

        filter1_matches['concat_matched_value'], filter1_matches['partname'] = zip(*filter1_matches.apply(
            lambda row: self._extract_matched_value(row, self.filter1_params['fields']), axis=1))
        filter2_matches['concat_matched_value'], filter2_matches['partname'] = zip(*filter2_matches.apply(
            lambda row: self._extract_matched_value(row, self.filter2_params['fields']), axis=1))

        matches_df = pd.concat([filter1_matches, filter2_matches]).reset_index(drop=True)

        # Group by RELATIONSHIP_ID and compare partnames
        grouped = matches_df.groupby('RELATIONSHIP_ID')
        valid_matches = grouped.filter(lambda x: len(x) == 2 and 
                                       self._compare_partnames(x['partname'].iloc[0], x['partname'].iloc[1]))

        if self.rule_params.amount_check_flags:
            for amount_field_flag, amount_flag_value in self.rule_params.amount_check_flags.items():
                valid_matches = valid_matches.groupby(['RELATIONSHIP_ID', 'concat_matched_value']).filter(
                    lambda group: self.check_amount_flag_condition(amount_check_mapping[amount_field_flag], amount_flag_value, group)
                )

        valid_matches['Rule_Id'] = self.rule_params.unique_rule_id
        print(f'Matches for {self.rule_params.unique_rule_id}: {len(valid_matches)}')
        return valid_matches
