import re
import pandas as pd
from itertools import combinations
from controllers.matching_matrix_controller.modules.strategies.base_strategy import BaseStrategy

class FieldValueStrategy(BaseStrategy):
    def __init__(self, rule_params, op_filters, strategy_id):
        super().__init__(rule_params, op_filters, strategy_id)
        self.field_value_field = self._get_field_value_field()

    def _get_field_value_field(self):
        for filter_id, filter_data in self.op_filters.items():
            for op_item in filter_data['op_items']:
                if op_item['field_value_flag']:
                    return op_item
        return None

    def validate_strategy(self):
        # Implement validation logic if needed
        return True

    def build_query(self, filter_data):
        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"COUNTRY": self.rule_params.category_code}},
                        {"terms": {"C_OR_D": [f"{filter_data['ls_flag']} {filter_data['dc_flag']}R"]}}
                    ]
                }
            }
        }

        if self.rule_params.set_id != 'ALL':
            query["query"]["bool"]["filter"].append({"terms": {"LOCAL_ACC_NO": self.rule_params.set_id}})

        if self.field_value_field:
            query["query"]["bool"]["filter"].append({
                "regexp": {self.field_value_field['field_name']: self.field_value_field['field_value_params']['field_value']['exp']}
            })

        return {
            'track_total_hits': True,
            **query,
            "_source": ["RELATIONSHIP_ID", "ITEM_ID", self.field_value_field['field_name']]
        }

    def find_matches(self):
        all_matches = []
        for filter_id, filter_data in self.op_filters.items():
            query = self.build_query(filter_data)
            scroll_id = None
            while True:
                scroll_id, hits = self.scroll_transactions(query, scroll_id)
                if not hits:
                    break
                all_matches.extend(hits)

        relationship_ids = set()
        matched_item_ids = {}

        for match in all_matches:
            source = match['_source']
            relationship_id = source['RELATIONSHIP_ID']
            relationship_ids.add(relationship_id)
            
            field_name = self.field_value_field['field_name']
            exp = self.field_value_field['field_value_params']['field_value']['exp']
            match_result = re.search(exp, source[field_name])
            
            if match_result:
                captured_group = match_result.group(1)
                match_value = max(re.findall(r'\d+', captured_group), key=len)  # Find the longest digit sequence
                if relationship_id not in matched_item_ids:
                    matched_item_ids[relationship_id] = {}
                matched_item_ids[relationship_id][source['ITEM_ID']] = match_value

        all_transactions = self._fetch_all_transactions(list(relationship_ids))
        df = pd.DataFrame(all_transactions)
        grouped = df.groupby('RELATIONSHIP_ID')

        matched_transactions = []
        for relationship_id, group in grouped:
            if relationship_id in matched_item_ids:
                for source_item_id, matched_value in matched_item_ids[relationship_id].items():
                    source_transaction = group[group['ITEM_ID'] == source_item_id]
                    matched_transaction = group[(group['ITEM_ID'] != source_item_id) & (group['ITEM_ID'] == matched_value)]
                    
                    if not source_transaction.empty and not matched_transaction.empty:
                        matched_transactions.extend(source_transaction.to_dict('records'))
                        matched_transactions.extend(matched_transaction.to_dict('records'))

        if matched_transactions:
            final_df = pd.DataFrame(matched_transactions)
            if self.rule_params.amount_check_flags:
                for amount_field_flag, amount_flag_value in self.rule_params.amount_check_flags.items():
                    final_df = final_df.groupby('RELATIONSHIP_ID').filter(
                        lambda group: self.check_amount_flag_condition(amount_field_flag, amount_flag_value, group)
                    )
            final_df['Rule_Id'] = self.rule_params.unique_rule_id
            return final_df

        return pd.DataFrame()

    def _fetch_all_transactions(self, relationship_ids):
        query = {
            "query": {
                "terms": {
                    "RELATIONSHIP_ID": relationship_ids
                }
            },
            "_source": selected_fields,
            "size": 10000
        }
        
        all_transactions = []
        scroll_id = None
        
        while True:
            scroll_id, hits = self.scroll_transactions(query, scroll_id)
            if not hits:
                break
            all_transactions.extend(hits)
        
        return all_transactions

    def check_amount_flag_condition(self, amount_field, amount_flag_value, group):
        # Implement the amount flag condition check logic here
        pass
