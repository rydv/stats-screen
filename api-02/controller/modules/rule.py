from typing import List, Dict
import pandas as pd
from collections import ChainMap
from filter import Filter
from expression_rule import ExpressionStrategy
from value_date_rule import ValueDateStrategy
from operation_rule import OperationStrategy
from client_name_rule import ClientNameStrategy
from field_value_rule import FieldValueStrategy
from perf_ref_rule import PerfRefStrategy

class Rule:
    def __init__(self, params: Dict, filters: List[Filter], op_mapping: Dict):
        self.rule_params = params
        self.filters = filters
        self.op_mapping = op_mapping
        self.strategies = self._instantiate_ops()

    def _instantiate_ops(self):
        strategies = {}
        for mapping_id, op_details in self.op_mapping.items():
            strategy_class = self._get_strategy_class(op_details['op_type'])
            if strategy_class:
                op_filters = op_details['filters']
                strategies[mapping_id] = strategy_class(self.rule_params, op_filters, mapping_id)
        return strategies

    def _get_strategy_class(self, op_type):
        strategy_map = {
            'expression_st': ExpressionStrategy,
            'value_date_st': ValueDateStrategy,
            'operation_st': OperationStrategy,
            'client_name_st': ClientNameStrategy,
            'field_value_st': FieldValueStrategy,
            'perf_ref_st': PerfRefStrategy
        }
        return strategy_map.get(op_type)

    def validate(self):
        for strategy in self.strategies.values():
            strategy.validate_strategy()

    def process_strategies(self):
        results = []
        for strategy_id, strategy in self.strategies.items():
            print(f"Processing strategy: {strategy_id}")
            matches = strategy.find_matches()
            matches['strategy_id'] = strategy_id
            results.append(matches)
        return pd.concat(results, ignore_index=True)

    def merge_and_process_results(self, results):
        df = pd.DataFrame(results)
        
        grouped = df.groupby('MATRIX_RELATIONSHIP_ID')
        
        all_strategy_ids = set(self.strategies.keys())
        
        or_and_flag = self.rule_params.or_and_flag.upper()
        
        final_results = []
        for _, group in grouped:
            strategy_ids_in_group = set(group['strategy_id'])
            
            if or_and_flag == 'AND':
                if not all_strategy_ids.issubset(strategy_ids_in_group):
                    continue
            elif or_and_flag == 'OR' or or_and_flag not in ['AND', 'OR']:
                if not strategy_ids_in_group:
                    continue
            
            item_groups = group.groupby('ITEM_ID')
            for _, item_group in item_groups:
                combined_match = {
                    'MATRIX_RELATIONSHIP_ID': item_group['MATRIX_RELATIONSHIP_ID'].iloc[0],
                    'ITEM_ID': item_group['ITEM_ID'].iloc[0],
                    'MATCHED_VALUE': '|'.join(item_group['MATCHED_VALUE']),
                    'EXACT_EXP_MATCH': [dict(ChainMap(*eval(m))) for m in item_group['EXACT_EXP_MATCH']]
                }
                # Add other fields from the first row
                for column in item_group.columns:
                    if column not in combined_match:
                        combined_match[column] = item_group[column].iloc[0]
                final_results.append(combined_match)
        
        return final_results

    def process(self):
        results = self.process_strategies()
        return self.merge_and_process_results(results)
