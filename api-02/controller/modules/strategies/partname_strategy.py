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

    def build_query(self, filter_data):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"COUNTRY": self.rule_params.category_code}}
                    ],
                    "should": [],
                    "minimum_should_match": 1
                }
            }
        }

        if self.rule_params.set_id != 'ALL':
            query["query"]["bool"]["must"].append({"terms": {"LOCAL_ACC_NO": self.rule_params.set_id}})

        tran_type = [f"{filter_data['ls_flag']} {filter_data['dc_flag']}R"] if filter_data['dc_flag'] != 'A' else [f"{filter_data['ls_flag']} CR", f"{filter_data['ls_flag']} DR"]
        query["query"]["bool"]["must"].append({"terms": {"C_OR_D": tran_type}})

        for op_item in filter_data['op_items']:
            query["query"]["bool"]["should"].append({"regexp": {op_item['field_name']: op_item['search_agg_exp']}})

        return query

    def _extract_matched_value(self, transaction, op_items):
        matched_values = []
        partname_values = []
        for op_item in op_items:
            if op_item['exp_flag'] or op_item['partname_flag']:
                match = re.search(op_item['search_agg_exp'], transaction[op_item['field_name']])
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
        all_matches = []
        for filter_id, filter_data in self.op_filters.items():
            query = self.build_query(filter_data)
            scroll_id = None
            while True:
                scroll_id, hits = self.scroll_transactions(query, scroll_id)
                if not hits:
                    break
                for match in hits:
                    match['filter_id'] = filter_id
                all_matches.extend(hits)

        df = pd.DataFrame(all_matches)
        grouped = df.groupby('RELATIONSHIP_ID')
        final_matches = []

        for rel_id, group in grouped:
            combinations_list = list(combinations(group.index, 2))
            for i, combo in enumerate(combinations_list):
                combo_df = group.loc[combo]
                
                if len(set(combo_df['filter_id'])) != 2:
                    continue
                
                for idx, row in combo_df.iterrows():
                    filter_data = self.op_filters[row['filter_id']]
                    row['concat_matched_value'], row['partname'] = self._extract_matched_value(row, filter_data['op_items'])
                    combo_df.loc[idx] = row

                if self._compare_partnames(combo_df['partname'].iloc[0], combo_df['partname'].iloc[1]):
                    if self.check_amount(combo_df):
                        for _, row in combo_df.iterrows():
                            match = row.to_dict()
                            match['MATRIX_RELATIONSHIP_ID'] = f"{rel_id}_{i+1}"
                            match['MATCHED_VALUES'] = f"{match['concat_matched_value']} | {match['partname']}"
                            final_matches.append(match)

        final_df = pd.DataFrame(final_matches)
        if len(final_df):
            final_df["Rule_Id"] = self.rule_params.unique_rule_id

        return final_df

    def check_amount(self, df):
        if self.rule_params.amount_check_flags:
            for amount_field_flag, amount_flag_value in self.rule_params.amount_check_flags.items():
                if not self.check_amount_flag_condition(amount_check_mapping[amount_field_flag], amount_flag_value, df):
                    return False
        return True

    def check_amount_flag_condition(self, amount_field, amount_flag_value, group):
        # Implement the amount flag condition check logic here
        pass
