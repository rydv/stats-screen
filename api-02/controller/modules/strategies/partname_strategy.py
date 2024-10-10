import re
import pandas as pd
from itertools import combinations
from controllers.matching_matrix_controller_01.config.config import *
from controllers.matching_matrix_controller_01.modules.strategies.base_strategy import BaseStrategy

class ClientNameStrategy(BaseStrategy):
    def __init__(self, rule_params, op_filters, strategy_id):
        super().__init__(rule_params, op_filters, strategy_id)

    def validate_strategy(self):
        # Implement validation logic if needed
        pass

    def _get_combinations(self, group_index):
        return list(combinations(group_index, 2))

    def _get_matched_values(self, transaction, op_filters):
        matched_values_list = []
        partname_values = []

        filter_id = transaction.get('filter_id')
        if filter_id not in op_filters:
            return [], ''
        
        for op_item in op_filters[filter_id]['op_items']:
            field_value = transaction[op_item['field_name']]
            matches = re.findall(op_item['search_agg_exp'], field_value)
            
            for match in matches:
                if isinstance(match, tuple):
                    if op_item['exp_flag'] or op_item['partname_flag']:
                        matched_values_list.extend(match[:-1])
                        partname_values.append(match[-1])
                    else:
                        matched_values_list.extend(match)
                else:
                    matched_values_list.append(match)
            
            if op_item['op_flag']:
                op_params = op_item['op_params']
                if op_params['op_type'] == 'REP':
                    matched_values_list = [value.replace(op_params['s1'], op_params['s2']) for value in matched_values_list]
        
        matched_values_list = list(set(matched_values_list))
        matched_values_list.sort()
        partname = " ".join(set(partname_values))
        return '/'.join(matched_values_list).strip().strip('|'), partname

    def _process_relationship_group(self, group):
        if len(set(group['filter_id'])) < len(self.op_filters) or not self.check_value_date(group) or not self.check_amount(group):
            return False, None
        
        group['MATCHED_VALUES'], group['PARTNAME'] = zip(*group.apply(lambda transaction: self._get_matched_values(transaction, self.op_filters), axis=1))
        
        if group['MATCHED_VALUES'].nunique() == 1 and self._compare_partnames(group['PARTNAME'].iloc[0], group['PARTNAME'].iloc[1]):
            return True, group
        
        return False, None

    def _compare_partnames(self, name1, name2):
        name1_parts = set(name1.lower().split())
        name2_parts = set(name2.lower().split())
        return bool(name1_parts & name2_parts)

    def find_matches(self):
        all_matches = []
        for filter_id, filter_data in self.op_filters.items():
            query = self.build_query(filter_data)
            scroll_id = None
            filter_matches = []
            while True:
                scroll_id, hits = self.scroll_transactions(query, scroll_id)
                if not hits:
                    break
                for match in hits:
                    match['filter_id'] = filter_id
                filter_matches.extend(hits)
            if not filter_matches:
                return pd.DataFrame()
            all_matches.extend(filter_matches)

        df = pd.DataFrame(all_matches)
        grouped = df.groupby('RELATIONSHIP_ID')
        final_matches = []
        for rel_id, group in grouped:
            group = group.drop_duplicates(subset='ITEM_ID')
            if len(group) <= 10:
                combinations_list = self._get_combinations(group.index)
                matched_item_ids = set()
                for combo in combinations_list:
                    combo_df = group.loc[list(combo)]
                    if any(item_id in matched_item_ids for item_id in combo_df['ITEM_ID']):
                        continue
                    out_flag, matched_group = self._process_relationship_group(combo_df)
                    if out_flag:
                        sorted_item_ids = '#'.join(sorted(matched_group['ITEM_ID'].astype(str)))
                        matched_group["MATRIX_RELATIONSHIP_ID"] = f"{self.rule_params.unique_rule_id}-{rel_id}-{sorted_item_ids}"
                        final_matches.append(matched_group)
                        matched_item_ids.update(matched_group['ITEM_ID'].tolist())
            elif self.rule_params.amount_check_flags['amount_flag'] == 'S' or self.rule_params.amount_check_flags['amount_flag'] == 'Same':
                sorted_group = group.sort_values('AMOUNT')
                amount_groups = sorted_group.groupby('AMOUNT')
                for amount, amount_group in amount_groups:
                    out_flag, matched_group = self._process_relationship_group(amount_group)
                    if out_flag:
                        sorted_item_ids = '#'.join(sorted(matched_group['ITEM_ID'].astype(str)))
                        matched_group['MATRIX_RELATIONSHIP_ID'] = f"{self.rule_params.unique_rule_id}-{rel_id}-{sorted_item_ids}"
                        final_matches.append(matched_group)
            else:
                pass
        final_df = pd.concat(final_matches).reset_index(drop=True)
        if len(final_df):
            final_df["MATCHED_VALUES"] = final_df["MATCHED_VALUES"] + " | " + final_df["PARTNAME"]
            del final_df['PARTNAME']
            final_df["Rule_Id"] = self.rule_params.unique_rule_id
        return final_df
