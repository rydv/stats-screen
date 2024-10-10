import re
import pandas as pd
from itertools import combinations
from controllers.matching_matrix_controller_01.config.config import *
from controllers.matching_matrix_controller_01.modules.strategies.base_strategy import BaseStrategy

class FieldValueStrategy(BaseStrategy):
    def __init__(self, rule_params, op_filters, strategy_id):
        super().__init__(rule_params, op_filters, strategy_id)
        self.field_value_field = self._get_field_value_field()
        self.master_filter = self._get_master_filter()

    def _get_master_filter(self):
        for filter_id, filter_data in self.op_filters.items():
            for op_item in filter_data['op_items']:
                if op_item['field_value_flag']:
                    return {'filter_id': filter_id, 'filter_data': filter_data}
        return None

    def _get_field_value_field(self):
        for filter_id, filter_data in self.op_filters.items():
            for op_item in filter_data['op_items']:
                if op_item['field_value_flag']:
                    return op_item
        return None

    def validate_strategy(self):
        # Implement validation logic if needed
        return True

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

    def _process_relationship_group(self, group):
        if not self.check_value_date(group) or not self.check_amount(group):
            c2 = (not self.check_value_date(group))
            c3 = (not self.check_amount(group))
            print(f'flag_checks: {c2}, {c3}')
            return False, None
        return True, group

    def find_matches(self):
        # get master filter matches
        all_matches = []
        master_filter_id = self.master_filter['filter_id']
        master_filter_data = self.master_filter['filter_data']
        query = self.build_query(master_filter_data)
        query = {
            'track_total_hits': True,
            **query,
            "_source": selected_fields
        }

        scroll_id = None
        while True:
            scroll_id, hits = self.scroll_transactions(query, scroll_id)
            if not hits:
                break
            all_matches.extend(hits)

        # get unique rel ids & generate rel id matched value mapping
                # get unique rel ids & generate rel id matched value mapping
        uniq_relationship_ids = set()
        rel_id_matched_value_mapping = {}

        for match in all_matches:
            relationship_id = match['RELATIONSHIP_ID']
            uniq_relationship_ids.add(relationship_id)
            
            field_name = self.field_value_field['field_name']
            exp = self.field_value_field['field_value_params']['field_value']['exp']
            match_result = re.search(exp, match[field_name])
            
            if match_result:
                captured_group = match_result.group(1)
                match_value = max(re.findall(r'\d+', captured_group), key=len)  # Find the longest digit sequence
                
                if relationship_id not in rel_id_matched_value_mapping:
                    rel_id_matched_value_mapping[relationship_id] = {}
                
                rel_id_matched_value_mapping[relationship_id][match['ITEM_ID']] = int(match_value)

        del all_matches
        print(rel_id_matched_value_mapping)

        # fetch all transactions
        all_transactions = self._fetch_all_transactions(list(uniq_relationship_ids))
        df = pd.DataFrame(all_transactions)

        # Look for groups satisfying rule conditions
        grouped = df.groupby('RELATIONSHIP_ID')
        matched_transactions = []
        matched_item_ids_set = set()

        for relationship_id, group in grouped:
            if relationship_id in rel_id_matched_value_mapping:
                for source_item_id, matched_value in rel_id_matched_value_mapping[relationship_id].items():
                    if source_item_id in matched_item_ids_set or matched_value in matched_item_ids_set:
                        continue
                    
                    source_transaction = group[group['ITEM_ID'] == source_item_id]
                    matched_transaction = group[(group['ITEM_ID'] != source_item_id) & (group['ITEM_ID'] == str(matched_value))]
                    
                    if not source_transaction.empty and not matched_transaction.empty:
                        source_transaction['filter_id'] = 'master-filter'
                        matched_transaction['filter_id'] = 'counter-filter'
                        
                        combined_group = pd.concat([source_transaction, matched_transaction]).reset_index(drop=True)
                        out_flag, processed_group = self._process_relationship_group(combined_group)
                        
                        if out_flag:
                            sorted_item_ids = '#'.join(sorted(processed_group['ITEM_ID'].astype(str)))
                            processed_group["MATRIX_RELATIONSHIP_ID"] = f"{self.rule_params.unique_rule_id}-{relationship_id}-{sorted_item_ids}"
                            processed_group["MATCHED_VALUES"] = matched_value
                            matched_transactions.append(processed_group)
                            matched_item_ids_set.update([source_item_id, matched_value])

        print(matched_transactions)

        if matched_transactions:
            final_df = pd.concat(matched_transactions).reset_index(drop=True)
            final_df['Rule_Id'] = self.rule_params.unique_rule_id
            return final_df

        return pd.DataFrame()

