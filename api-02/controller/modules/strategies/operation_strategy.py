import re
import pandas as pd
from itertools import combinations
from controllers.matching_matrix_controller_01.config.config import *
from controllers.matching_matrix_controller_01.modules.strategies.base_strategy import BaseStrategy

class OperationStrategy(BaseStrategy):
    def __init__(self, rule_params, op_filters, strategy_id):
        super().__init__(rule_params, op_filters, strategy_id)

    def validate_strategy(self):
        # Implement validation logic if needed
        pass

    def _get_combinations(self, group_index):
        return [combo for i in range(2, len(group_index)+1) for combo in combinations(group_index, i)]

    def _get_matched_values(self, transaction, op_filters):
        matched_values_list = []

        filter_id = transaction.get('filter_id')
        if filter_id not in op_filters:
            return []
        
        print(f'{filter_id} matches')
        print(f"Total op items: {len(op_filters[filter_id]['op_items'])}")
        cnt = 0
        for op_item in op_filters[filter_id]['op_items']:
            print(f"Op Item: {cnt}")
            print(f"Op Item - Field: {op_item['field_name']}")

            cnt+=1
            field_value = transaction[op_item['field_name']]
            print(f"Op Item - Field-Value: {field_value}")
            print(f"Op Item - Field-Exp: {op_item['search_agg_exp']}")
            matches = re.findall(op_item['search_agg_exp'], field_value)
            print(f"findall matches: {matches}")
            if not re.search(r"\([^)]*\)", op_item['search_agg_exp']):
                # matched_values_list.extend(['string-match'])
                continue
            matched_values = []
            for match in matches:
                if isinstance(match, tuple):
                    matched_values.extend(match)
                else:
                    matched_values.append(match)
            if op_item['op_flag']:
                op_params = op_item['op_params']
                if op_params['op_type'] == 'REP':
                    matched_values = [value.replace(op_params['s1'], op_params['s2']) for value in matched_values]
            print(f"Fixed matches for item: {matched_values}")
            matched_values_list.extend(matched_values)
            # cnt += 1
        matched_values_list = list(set(matched_values_list))
        matched_values_list.sort()
        print(f"Final matched value: '{'/'.join(matched_values_list).strip().strip('|')}'")
        return '/'.join(matched_values_list).strip().strip('|')

    def _process_relationship_group(self, group):
        print("--")
        print(group)
        if len(set(group['filter_id'])) < len(self.op_filters) or not self.check_value_date(group) or not self.check_amount(group):
            print(len(set(group['filter_id'])))
            print(len(self.op_filters))
            c1 = (len(set(group['filter_id'])) < len(self.op_filters))
            c2 = (not self.check_value_date(group))
            c3 = (not self.check_amount(group))
            print(c1, c2, c3)
            return False, None
        group['MATCHED_VALUES'] = group.apply(lambda transaction: self._get_matched_values(transaction, self.op_filters), axis=1)
        print(group['MATCHED_VALUES'])
        if group['MATCHED_VALUES'].nunique() == 1:
            return True, group
        print("--")
        return False, None

    def find_matches(self):
        all_matches = []
        for filter_id, filter_data in self.op_filters.items():
            print(f"Looking matches for - {filter_id}")
            print(f"Filter Info")
            print(f"Is_flag: {filter_data['is_flag']}")
            print(f"d_flag: {filter_data['dc_flag']}")
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
                print(f"No matches found for {filter_id}")
                return pd.DataFrame()  # Return empty DataFrame if no matches for a filter
            all_matches.extend(filter_matches)

        print('op filter')
        df = pd.DataFrame(all_matches)
        print(df[['ITEM_ID', 'RELATIONSHIP_ID', 'SFIELD_8', 'SFIELD_9', 'REFERENCE', 'STRING_1', 'filter_id']])
        print(df[['ITEM_ID', 'RELATIONSHIP_ID', 'SFIELD_8', 'filter_id']].sort_values(by='RELATIONSHIP_ID'))
        grouped = df.groupby('RELATIONSHIP_ID')
        final_matches = []
        grp_count = 0
        for rel_id, group in grouped:
            group = group.drop_duplicates(subset='ITEM_ID')
            grp_count += 1
            if len(group) <= 10:
                combinations_list = self._get_combinations(group.index)
                print(f"groups count: {len(combinations_list)}")
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
                print(f'amount groups count: {len(amount_groups)}')
                for amount, amount_group in amount_groups:
                    out_flag, matched_group = self._process_relationship_group(amount_group)
                    if out_flag:
                        sorted_item_ids = '#'.join(sorted(matched_group['ITEM_ID'].astype(str)))
                        matched_group['MATRIX_RELATIONSHIP_ID'] = f"{self.rule_params.unique_rule_id}-{rel_id}-{sorted_item_ids}"
                        final_matches.append(matched_group)
            else:
                pass
        print('--')
        final_df = pd.concat(final_matches).reset_index(drop=True)
        if len(final_df):
            print(final_df[['ITEM_ID', 'RELATIONSHIP_ID', 'MATCHED_VALUES']])
            del final_df['MATCHED_VALUES']
            final_df["Rule_Id"] = self.rule_params.unique_rule_id
            print(f"Matches for rule {self.rule_params.unique_rule_id}: {len(final_df)}")
        return final_df