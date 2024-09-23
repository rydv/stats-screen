import re
import pandas as pd
from itertools import combinations
from controllers.matching_matrix_controller.modules.strategies.base_strategy import BaseStrategy

class PerfRefStrategy(BaseStrategy):
    def __init__(self, rule_params, op_filters, strategy_id):
        super().__init__(rule_params, op_filters, strategy_id)

    def validate_strategy(self):
        # Implement validation logic if needed
        return True

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

    def find_matches(self):
        all_matches = []
        for filter_id, filter_data in self.op_filters.items():
            query = self.build_query(filter_data)
            matches = self.scroll_transactions(query)
            for match in matches:
                match['filter_id'] = filter_id
            all_matches.extend(matches)

        df = pd.DataFrame(all_matches)
        grouped = df.groupby('RELATIONSHIP_ID')
        
        final_matches = []
        for rel_id, group in grouped:
            combinations_list = list(combinations(group.index, len(self.op_filters)))
            for i, combo in enumerate(combinations_list):
                combo_df = group.loc[combo]
                
                # Check if there's at least one transaction from each filter
                if len(set(combo_df['filter_id'])) != len(self.op_filters):
                    continue
                
                # Drop duplicates on 'ITEM_ID'
                combo_df = combo_df.drop_duplicates(subset='ITEM_ID')
                
                # Value date check
                if not self.check_value_date(combo_df):
                    continue
                
                # Amount check
                if not self.check_amount(combo_df):
                    continue
                
                # Find common patterns
                common_patterns = self.find_common_patterns(combo_df)
                if common_patterns:
                    for _, row in combo_df.iterrows():
                        match = row.to_dict()
                        match['MATRIX_RELATIONSHIP_ID'] = f"{rel_id}_{i+1}"
                        match['MATCHED_VALUES'] = common_patterns
                        final_matches.append(match)

        return pd.DataFrame(final_matches)

    def check_value_date(self, df):
        if self.rule_params.value_date_flag.upper() == "YES":
            return df['VALUE_DATE'].nunique() == 1
        elif self.rule_params.value_date_flag.upper() == "NO":
            return df['VALUE_DATE'].nunique() > 1
        return True

    def check_amount(self, df):
        if self.rule_params.amount_check_flags:
            for amount_field_flag, amount_flag_value in self.rule_params.amount_check_flags.items():
                if not self.check_amount_flag_condition(amount_field_flag, amount_flag_value, df):
                    return False
        return True

    def check_amount_flag_condition(self, amount_field, amount_flag_value, group):
        # Implement the amount flag condition check logic here
        pass

    def find_common_patterns(self, df):
        # Implement the logic to find common patterns across the fields
        pass
