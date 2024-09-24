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
                common_patterns = self._process_relationship_group(combo_df.to_dict('records'))
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

    def _process_relationship_group(self, group):
        matches = []

        op_info=self.op_filters[group[0]['filter-1']]['op_items'][0]

        def join_concated_values(transaction, op_filters):
            filter_id = transaction.get('filter_id')
            if filter_id not in op_filters:
                return ''
            return '|'.join(
                transaction.get(op_item['field_name'], '')
                for op_item in op_filters[filter_id]['op_items']
            )

        group['concated_values'] = group.apply(lambda transaction: join_concated_values(transaction, self.op_filters), axis=1)

        # for field_id, field_info in self.filter_mapping.items():
        all_concated_values = [t['concated_values'] for t in group]
        common_substrings = self._find_top_5_common_substrings(all_concated_values, op_info['perf_ref_params'])
        
        valid_substrings = [
            substr for substr in common_substrings 
            if '|' not in substr and 
            self._check_substring_length(substr, op_info.get('perf_ref_params', ''))
        ]

        if valid_substrings:
            search_agg_exp = op_info.get('search_agg_exp', '')
            if search_agg_exp:
                matching_substrings = [
                    substr for substr in valid_substrings 
                    if re.search(search_agg_exp, substr)
                ]
                if matching_substrings:
                    matches = matching_substrings
            else:
                matches = valid_substrings

        return matches

    def _check_substring_length(self, substring, params):
        length = len(substring)
        min_length = params.get('min_length', 5)
        max_length = params.get('max_length', 15)
        exact_length = params.get('exact_length')
        
        if exact_length:
            return length == exact_length
        return min_length <= length <= max_length

    def _find_top_5_common_substrings(self, strings, params, exp=None):
        if not strings:
            return []

        common_substrings = set(self._get_substrings(strings[0], params))
        for s in strings[1:]:
            common_substrings &= set(self._get_substrings(s, params))

        if exp is not None:
            matching_substrings = [substr for substr in common_substrings if re.search(exp, substr)]
            sorted_substrings = sorted(matching_substrings, key=len, reverse=True)
        else:
            sorted_substrings = sorted(list(common_substrings), key=len, reverse=True)

        result = []
        for substr in sorted_substrings:
            if not any(substr in s for s in result):
                result.append(substr)
                if len(result) == 5:
                    break

        return result

    def _get_substrings(self, s, params):
        min_len = int(params.get('min_length', 5)) if params.get('min_length') is not None else 5
        max_len = int(params.get('max_length', 15)) if params.get('max_length') is not None else None
        exact_len = int(params.get('exact_length')) if params.get('exact_length') is not None else None

        if exact_len:
            return [s[i:i+exact_len] for i in range(len(s)-exact_len+1) if '|' not in s[i:i+exact_len]]
        else:
            return [s[i:j] for i in range(len(s)) for j in range(i + min_len, len(s) + 1) if '|' not in s[i:j] and (max_len is None or j - i <= max_len)]
