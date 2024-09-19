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
        self.op_field = self._get_op_field()

    def _get_op_field(self):
        for field in self.filter1_params['fields']:
            if field.op_flag:
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

            if self.op_field:
                query["query"]["bool"]["filter"].append({
                    "regexp": {self.op_field.name: self.op_field.search_agg_exp}
                })

            return {
                'track_total_hits': True,
                **query,
                "_source": selected_fields
            }
        except Exception as e:
            raise ValueError(f"Failed to format query for the operation rule: {e}")

    def _scroll_transactions(self, query, scroll_id):
        try:
            es = es_connect()
            if scroll_id:
                response = es.scroll(scroll_id=scroll_id, scroll='1m')
            else:
                response = es.search(index=matched_data_index, body=query, scroll='1m', size=10000)

            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            return scroll_id, hits
        except Exception as e:
            raise ValueError(f'Failed to get matches for the filter: {e}')

    def _apply_operation(self, value):
        op_params = self.op_field.op_params
        if op_params['op_type'] == 'REP':
            return value.replace(op_params['s1'], op_params['s2'])
        return value

    def _process_transaction(self, transaction):
        field_name = self.op_field.name
        exp = self.op_field.search_agg_exp
        match = re.search(exp, transaction[field_name])
        
        if match:
            extracted_value = match.group(1)  # Assuming the value to be operated on is in the first capturing group
            operated_value = self._apply_operation(extracted_value)
            return operated_value
        return None

    def find_matches(self) -> pd.DataFrame:
        query = self._filter_query_formatter()
        scroll_id = None
        matched_transactions = []
        es = es_connect()

        while True:
            scroll_id, hits = self._scroll_transactions(query, scroll_id)
            if not hits:
                break

            for hit in hits:
                transaction = hit['_source']
                operated_value = self._process_transaction(transaction)
                if operated_value:
                    transaction['OPERATED_VALUE'] = operated_value
                    matched_transactions.append(transaction)

        if matched_transactions:
            final_df = pd.DataFrame(matched_transactions)
            if self.rule_params.amount:
                final_df = final_df.groupby('RELATIONSHIP_ID').filter(
                    lambda group: self.check_amount_flag_condition('AMOUNT', self.rule_params.amount, group)
                )
            final_df['Rule_Id'] = self.rule_params.unique_rule_id
            return final_df

        return pd.DataFrame()
