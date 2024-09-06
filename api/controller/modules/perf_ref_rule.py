import re
import pandas as pd
from typing import List, Dict
from collections import defaultdict
from difflib import SequenceMatcher

from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.config.elasticsearch_client import es_connect
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.base_rule import BaseRule

class Rule(BaseRule):
    def __init__(self, rule_params: RuleParams, l_s: str, d_c: str, fields: List[Field]):
        super().__init__(rule_params, l_s, d_c, fields)

    def valid_rule_scenario(self):
        """Validate that the rule has the required filter values set for PerfRef processing."""
        if not self.filter1 or not self.filter2:
            return False
        # Check if the necessary fields for PerfRef are present
        return 'PerfectReference' in self.parsing_info['filter1'] and 'PerfectReference' in self.parsing_info['filter2']

    def _find_top_5_common_substrings(self, ref1: str, ref3: str):
        """Find the top 5 longest common substrings between ref1 and ref3."""
        match = SequenceMatcher(None, ref1, ref3).get_matching_blocks()
        substrings = sorted([ref1[m.a:m.a+m.size] for m in match if m.size >= 5], key=len, reverse=True)
        return substrings[:5]  # Return top 5 longest substrings

    def _validate_and_mark(self, txn_group, min_len=5, max_len=15):
        """Validate and mark relationship groups based on common substrings."""
        if len(txn_group) != 2:
            return False, []  # Only consider groups with exactly two transactions

        # Extract the REFERENCE field from both transactions
        ref1 = txn_group[0].get('REFERENCE', '')
        ref3 = txn_group[1].get('REFERENCE', '')

        # Ensure both references are provided and non-empty
        if not ref1 or not ref3:
            return False, []

        # Find common substrings between the two references
        common_substrings = self._find_top_5_common_substrings(ref1, ref3)

        # Filter substrings based on the length criteria
        valid_substrings = [substring for substring in common_substrings if min_len <= len(substring) <= max_len]

        # Return True if any valid substrings exist, along with the list of valid substrings
        return bool(valid_substrings), valid_substrings

    def _group_by_trans_by_rel(self, transactions):
        """Group transactions by RELATIONSHIP_ID."""
        grouped_transactions = defaultdict(list)
        for txn in transactions:
            relationship_id = txn['RELATIONSHIP_ID']
            grouped_transactions[relationship_id].append(txn)
        return grouped_transactions

    def _scroll_transactions(self, query, scroll_id):
        try:
            es = es_connect()
            if scroll_id:
                response = es.scroll(scroll_id=scroll_id, scroll='1m')
            else:
                response = es.search(index=matched_data_index, body=query, scroll='1m', size=10000)

            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            transactions = [hit['_source'] for hit in hits]
            return scroll_id, transactions
        except Exception as e:
            raise ValueError(f'Failed to get matches for the filter: {e}')

    def find_matches(self) -> pd.DataFrame:
        query = self._filter_query_formatter()
        scroll_id = None
        matched_transactions = []

        while True:
            scroll_id, transactions = self._scroll_transactions(query, scroll_id)
            if not transactions:
                break

            grouped_transactions = self._group_by_trans_by_rel(transactions)

            # Process each group
            for relationship_id, txn_group in grouped_transactions.items():
                is_matched, matched_substrings = self._validate_and_mark(txn_group)
                if is_matched:
                    txn_group_df = pd.DataFrame(txn_group)
                    txn_group_df['MATCHED_VALUE'] = ', '.join(matched_substrings)
                    matched_transactions.append(txn_group_df)

        # Concatenate all DataFrames in the list into a single DataFrame
        if matched_transactions:
            final_df = pd.concat(matched_transactions, ignore_index=True)

            # Apply amount flag filter if self.amount_flag is set
            if self.rule_params.amount:
                final_df = final_df.groupby('RELATIONSHIP_ID').filter(
                    lambda group: self.check_amount_flag_condition('AMOUNT', self.rule_params.amount, group)
                )

            # Reset index
            final_df.reset_index(drop=True, inplace=True)
            final_df['Rule_Id'] = self.rule_params.unique_rule_id
            return final_df

        return pd.DataFrame()  # Return an empty DataFrame if no matches found
