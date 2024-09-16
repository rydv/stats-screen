import pandas as pd
from rule_builder import RuleBuilder
from rule_params import RuleParams
from field import Field

def process_rules(file_path):
    csv_data = pd.read_csv(file_path).fillna("")
    rule_builder = RuleBuilder()
    rules = []

    current_rule_id = None
    for _, row in csv_data.iterrows():
        if current_rule_id != row['unique_rule_id']:
            if current_rule_id is not None:
                rules.append(rule_builder.build())
            current_rule_id = row['unique_rule_id']
            rule_params = RuleParams(**row)
            rule_builder.set_params(rule_params)

        fields = [Field(col, row[col]) for col in ['ref1', 'ref2', 'ref3', 'ref4']]
        rule_builder.add_filter(fields)

    if current_rule_id is not None:
        rules.append(rule_builder.build())

    return rules