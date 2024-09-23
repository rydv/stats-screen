import re
import pandas as pd
from itertools import combinations
from controllers.matching_matrix_controller.modules.strategies.base_strategy import BaseStrategy

class ExpressionStrategy(BaseStrategy):
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

    def process_matches(self, matches):
        processed_matches = []
        for match in matches:
            processed_match = match.copy()
            matched_values_list = []
            for filter_id, filter_data in self.op_filters.items():
                for op_item in filter_data['op_items']:
                    field_value = match.get(op_item['field_name'], '')
                    matched_values = re.findall(op_item['search_agg_exp'], field_value)
                    matched_values_list.extend(matched_values)
            processed_match['matched_value'] = list(set(matched_values_list))
            processed_matches.append(processed_match)
        return processed_matches

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
                processed_matches = self.process_matches([hit['_source'] for hit in hits])
                for match in processed_matches:
                    match['filter_id'] = filter_id
                filter_matches.extend(processed_matches)
                if not filter_matches:
                    print(f"No matches found for filter ID: {filter_id}")
                    return pd.DataFrame()  # Return empty DataFrame if no matches for a filter
            all_matches.extend(filter_matches)
            print(f"Count for filter {filter_id}: {len(filter_matches)}")

        df = pd.DataFrame(all_matches)
        grouped = df.groupby('RELATIONSHIP_ID')
        
        final_matches = []
        for rel_id, group in grouped:
            # Remove duplicate entries based on ITEM_ID
            group = group.drop_duplicates(subset='ITEM_ID')
            
            if len(group) <= 20:
                combinations_list = list(combinations(group.index, len(self.op_filters)))
                for i, combo in enumerate(combinations_list):
                    combo_df = group.loc[combo]
                    filter_ids = set(combo_df['filter_id'])
                    if len(filter_ids) == len(self.op_filters):
                        common_values = set.intersection(*[set(v) for v in combo_df['matched_value'].values if v])
                        if common_values:
                            for _, row in combo_df.iterrows():
                                match = row.to_dict()
                                match['MATRIX_RELATIONSHIP_ID'] = f"{rel_id}_{i+1}"
                                match['MATCHED_VALUES'] = list(common_values)
                                final_matches.append(match)
            elif self.check_for_sam_amount_flags():
                sorted_group = group.sort_values('AMOUNT')
                amount_groups = sorted_group.groupby('AMOUNT')
                for amount, amount_group in amount_groups:
                    filter_ids = set(amount_group['filter_id'])
                    if len(filter_ids) == len(self.op_filters):
                        common_values = set.intersection(*[set(v) for v in amount_group['matched_value'].values if v])
                        if common_values:
                            for _, row in amount_group.iterrows():
                                match = row.to_dict()
                                match['MATRIX_RELATIONSHIP_ID'] = f"{rel_id}_{amount}"
                                match['MATCHED_VALUES'] = list(common_values)
                                final_matches.append(match)
            else:
                pass

        return pd.DataFrame(final_matches)