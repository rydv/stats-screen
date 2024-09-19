import pandas as pd
from rule_builder import RuleBuilder
from rule_params import RuleParams
from field import Field
import traceback

def process_rules(file_path):
    csv_data = pd.read_csv(file_path).fillna("")
    rule_builder = RuleBuilder()
    valid_rules = []
    rejected_rules = []

    current_rule_id = None
    for _, row in csv_data.iterrows():
        if current_rule_id != row['unique_rule_id']:
            if current_rule_id is not None:
                built_rule = rule_builder.build()
                if built_rule:
                    valid_rules.append(built_rule)
                else:
                    rejected_rules.append({"unique_rule_id": current_rule_id, "reason": "Failed to build rule"})
            current_rule_id = row['unique_rule_id']
            try:
                rule_params = RuleParams(
                    unique_rule_id=row['unique_rule_id'],
                    category_code=row['category_code'],
                    set_id=row['set_id'],
                    amount_check_flags={flag: row[flag] for flag in amount_columns_mapping.keys() if row[flag]},
                    value_date_flag=row['value_date_flag'],
                    or_and_flag=row['or_and_flag'],
                )
                rule_builder.set_params(rule_params)
            except ValidationError as e:
                rejected_rules.append({"unique_rule_id": row['unique_rule_id'], "reason": str(e)})
                continue

        l_s = row['ls_flag']
        d_c = row['dc_flag']
        reffields = list(set(row.keys()) & set(col_mapping.keys()))
        fields = [Field(col_mapping[col], col, row[col]) for col in reffields]
        rule_builder.add_filter(l_s, d_c, fields)

    if current_rule_id is not None:
        built_rule = rule_builder.build()
        if built_rule:
            valid_rules.append(built_rule)
        else:
            rejected_rules.append({"unique_rule_id": current_rule_id, "reason": "Failed to build rule"})

    # print(f"'valid_rules': {valid_rules}, 'rejected_rules': {rejected_rules}")

    rule_matches = []
    # matched_rels_all = []

    matches_df = pd.DataFrame()
    print("Processing valid rules...")
    # for rule_type, rules in valid_rules.items():
    for rule in valid_rules:
        print(f"Rule: {rule.rule_params.unique_rule_id}")
        matches_df = rule.find_matches()
        if len(matches_df):
            rule_matches.append(matches_df)

    try:
        if len(rule_matches):
            print("Aggregating matches")
            res_df = pd.concat(rule_matches)
            res_df.reset_index(drop=False, inplace=True)
            res_df.sort_values(by='RELATIONSHIP_ID', inplace=True)
            res_df.drop_duplicates(subset='ITEM_ID', keep='first', inplace=True)
            res_df.to_csv(f'{reports_path}/manual_rule_analysis_report_singapore_20240702.csv', index=False)
            # report_name = 'manual_rule_analysis_report_singapore_20240702.csv'
            run_summary = res_df['Rule_Id'].value_counts().to_dict()
            run_summary = {k: int(v) for k, v in run_summary.items()}
        else:
            print("Nothing to concat.")
            res_df = pd.DataFrame()
            run_summary = {}
    except Exception as e:
        print(f'Failed to aggregate matches due to error: {e}')
        print(traceback.format_exc())
        res_df = pd.DataFrame()
        run_summary = {}

    return {
        'status': True,
        'output': {
            "matches": res_df,
            'valid_rules': valid_rules,
            'rejected_rules': rejected_rules,
            "run_summary": {
                "matches": f"{len(run_summary)}/{sum(len(rules) for rules in valid_rules.values())}",
                "matches_count": run_summary,
            }
        },
        'error_details': None
    }