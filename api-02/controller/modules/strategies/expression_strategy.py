from controllers.matching_matrix_controller.modules.strategies.base_strategy import BaseStrategy
import re
import pandas as pd

class ExpressionStrategy(BaseStrategy):
    def __init__(self, rule_params, op_mapping, strategy_id):
        super().__init__(rule_params, op_mapping, strategy_id)
        self.expression_ops = self._create_expression_operations()

    def _create_expression_operations(self):
        expression_ops = []
        for op in self.op_mapping:
            if op['op_type'] == '|EXP|':
                expression_ops.append(ExpressionOperation(op['field_name'], op['content']))
        return expression_ops

    def validate_strategy(self):
        for op in self.expression_ops:
            if not op.validate():
                raise ValueError(f"Invalid regular expression for field {op.field_name}")

    def build_query(self):
        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"COUNTRY": self.rule_params.category_code}}
                    ]
                }
            }
        }

        if self.rule_params.set_id != 'ALL':
            query["query"]["bool"]["filter"].append({"terms": {"LOCAL_ACC_NO": self.rule_params.set_id}})

        if self.rule_params.d_c != 'A':
            tran_type = [f"{self.rule_params.l_s} {self.rule_params.d_c}R"]
        else:
            tran_type = [f"{self.rule_params.l_s} CR", f"{self.rule_params.l_s} DR"]
        
        query["query"]["bool"]["filter"].append({"terms": {"C_OR_D": tran_type}})

        return query

    def process_matches(self, matches):
        df = pd.DataFrame(matches)
        df['concat_matched_value'] = df.apply(self._extract_matched_value, axis=1)
        df['Rule_Id'] = self.rule_params.unique_rule_id
        return df

    def _extract_matched_value(self, row):
        matched_values = []
        for op in self.expression_ops:
            match = op.apply(row)
            if match:
                if isinstance(match[0], tuple):
                    matched_values.extend(list(match[0]))
                else:
                    matched_values.append(match[0])
        matched_values.sort()
        return " | ".join(matched_values)

    def find_matches(self):
        query = self.build_query()
        all_matches = []
        scroll_id = None

        while True:
            scroll_id, transactions = self.scroll_transactions(query, scroll_id)
            if not transactions:
                break
            all_matches.extend(transactions)

        matches_df = self.process_matches(all_matches)

        if self.rule_params.amount_check_flags:
            for amount_field_flag, amount_flag_value in self.rule_params.amount_check_flags.items():
                matches_df = matches_df.groupby(['RELATIONSHIP_ID', 'concat_matched_value']).filter(
                    lambda group: self.check_amount_flag_condition(amount_check_mapping[amount_field_flag], amount_flag_value, group)
                )

        print(f'Matches for {self.rule_params.unique_rule_id}: {len(matches_df)}')
        return matches_df

class ExpressionOperation:
    def __init__(self, field_name, content):
        self.field_name = field_name
        self.pattern = content

    def validate(self):
        try:
            re.compile(self.pattern)
            return True
        except re.error:
            return False

    def apply(self, data):
        return re.findall(self.pattern, data[self.field_name])
