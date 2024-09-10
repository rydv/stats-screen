import re
import pandas as pd
from typing import List, Dict
from abc import ABC, abstractmethod
from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams

class BaseRule(ABC):
    def __init__(self, rule_params: RuleParams, l_s: str, d_c: str, fields: List[Field]):
        self.rule_params = rule_params
        self.parsing_info = {"filter1": {}, "filter2": {}}  # Dictionary to store parsed rule cases
        self.filter1_params = {
            'l_s': l_s,
            'd_c': d_c,
            'fields': fields
        }
        self.filter2 = {}
        self.filter_mapping={}
        self._update_parsing_info('filter1', fields)

    def add_filter2(self, l_s: str, d_c: str, fields: List[Field]):
        self.filter2_params = {
            'l_s': l_s,
            'd_c': d_c,
            'fields': fields
        }
        self._update_parsing_info('filter2', fields)

    def _update_parsing_info(self, filter_key, fields: List['Field']):
        """Update parsing information dictionary based on the field's flags."""
        for field in fields:
            if field.perf_ref_flag:
                self.parsing_info[filter_key].setdefault('PerfectReference', []).append(field.name)
            if field.valdt_flag:
                self.parsing_info[filter_key].setdefault('ValueDate', []).append(field.name)
            if field.op_flag:
                self.parsing_info[filter_key].setdefault('Operation', []).append(field.name)
            # Add more cases as needed based on the flags

    def _exp_flag_check(self):
        filter1_flag = any([field.exp_flag for field in self.filter1_params['fields']])
        filter2_flag = any([field.exp_flag for field in self.filter2_params['fields']])
        return (filter1_flag & filter2_flag)
    
    def _create_field_condition(self, field):
            if field.value:
                if not field.fm_flag:
                    expression = f'.*{field.search_agg_exp}.*'
                else:
                    expression = field.search_agg_exp
                return {"regexp": {field.name: expression}}
            return None

    def check_amount_flag_condition(self, field_name: str, flag_value: str, relationship_group: pd.DataFrame) -> bool:
        """Checks the AMOUNT field based on the amount_flag condition for the relationship group."""
        # Separate credit and debit transactions
        credit_txns = relationship_group[relationship_group['C_OR_D'].str.contains('CR')]
        debit_txns = relationship_group[relationship_group['C_OR_D'].str.contains('DR')]

        # Ensure there is at least one credit and one debit transaction
        if credit_txns.empty or debit_txns.empty:
            return False

        # Calculate the net amount for credit and debit transactions

        credit_amount = credit_txns[field_name].astype(float).sum()
        debit_amount = debit_txns[field_name].astype(float).sum()

        # Net difference between credit and debit amounts
        net_diff = abs(credit_amount - debit_amount)

        print(f'Net diff: {net_diff}, trn count: {len(relationship_group)}')

        # Handle the flag conditions
        if flag_value == 'Same':
            return credit_amount == debit_amount
        elif flag_value.startswith('Different'):
            # Split the flag (e.g., 'Different|LE|50' → 'Different', 'LE', '50')
            _, operator, threshold = flag_value.split('|')
            threshold = float(threshold)

            # Perform the checks based on the operator
            if operator == 'LE':
                return net_diff <= threshold
            elif operator == 'L':
                return net_diff < threshold
            elif operator == 'GE':
                return net_diff >= threshold
            elif operator == 'G':
                return net_diff > threshold

        return False

    @abstractmethod
    def valid_rule_scenario(self):
        """Abstract method for validating if corresponding rule cases are present."""
        pass

    @abstractmethod
    def find_matches(self):
        """Abstract method for finding matches for the rule."""
        pass
