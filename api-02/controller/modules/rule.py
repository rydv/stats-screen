from typing import List, Dict
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

    def process(self, data):
        results = []
        for strategy in self.strategies.values():
            results.extend(strategy.find_matches())
        return results
