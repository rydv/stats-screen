import os
import csv
import pandas as pd
from typing import List
from pydantic import ValidationError
from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.expression_rule import Rule as ExpRule
from controllers.matching_matrix_controller.modules.value_date_rule import Rule as ValdtRule
from controllers.matching_matrix_controller.modules.perf_ref_rule import Rule as PerfRefRule
from controllers.matching_matrix_controller.modules.client_name_rule import Rule as ClientNameRule

def validate_rule(rule):
    try:
        rule.validate_ref_values()
        return True, None
    except ValueError as e:
        return False, str(e)

def valdt_type_check(fields: List[Field]):
    return any([field.valdt_flag for field in fields])

def operation_type_check(fields: List[Field]):
    return any([field.op_flag for field in fields])

def identify_rule_type(fields: List[Field]):
    rule_type = None
    if any([field.perf_ref_flag for field in fields]):
        rule_type = 'perfect_ref'
    elif any([field.valdt_flag for field in fields]):
        rule_type = 'value_date'
    elif any([field.op_flag for field in fields]):
        rule_type = 'operation'
    elif any([field.partname_flag for field in fields]):
        rule_type = 'client_name'
    return rule_type

def process_rules(file):
    valid_rules = {
        "exact": [],
        "expression": [],
        "client_name": []
    }
    rejected_rules = []

    inp_file_name = file['_source']['uploadedFileName']
    file_path = os.path.join(input_path, inp_file_name)
    print(file_path)

    if not os.path.isfile(file_path):
        return {'status': False, 'output': None, 'error_details': f'File does not exist: {file_path}'}

    csv_data = pd.read_csv(file_path).fillna("")
    data_dict = csv_data.to_dict(orient='records')

    current_rule = None

    for row in data_dict:
        if row['unique_rule_id'] in [item['unique_rule_id'] for item in rejected_rules]:
            print(f"{row['unique_rule_id']} is rejected!")
            continue

        try:
            rule_params = RuleParams(
                unique_rule_id=row['unique_rule_id'],
                category_code=row['category_code'],
                set_id=row['set_id'],
                amount_check_flags={flag: row[flag] for flag in amount_columns_mapping.keys() if row[flag]},
                value_date=row['value_date_flag'],
            )
        except ValidationError as e:
            rejected_rules.append({"unique_rule_id": row['unique_rule_id'], "reason": str(e)})
            continue

        l_s = row['ls_flag']
        d_c = row['dc_flag']
        reffields = list(set(row.keys()) & set(col_mapping.keys()))
        fields = [Field(col_mapping[col], col, row[col]) for col in reffields]

        if current_rule and current_rule.rule_params.unique_rule_id == rule_params.unique_rule_id:
            current_rule.add_filter2(l_s, d_c, fields)
            valid_rules[row['rule_type']].append(current_rule)
        else:
            rule_type = identify_rule_type(fields)
            if rule_type == 'perfect_ref':
                current_rule = PerfRefRule(rule_params, l_s, d_c, fields)
            elif rule_type == 'value_date':
                current_rule = ValdtRule(rule_params, l_s, d_c, fields)
            elif rule_type == 'operation':
                current_rule = ValdtRule(rule_params, l_s, d_c, fields)
            elif rule_type == 'client_name':
                current_rule = ClientNameRule(rule_params, l_s, d_c, fields)
            else:
                current_rule = ExpRule(rule_params, l_s, d_c, fields)

    print(f"'valid_rules': {valid_rules}, 'rejected_rules': {rejected_rules}")

    rule_matches = []
    matched_rels_all = []

    matches_df = pd.DataFrame()
    print("Processing valid rules...")
    for rule_type, rules in valid_rules.items():
        for rule in rules:
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
            report_name = 'manual_rule_analysis_report_singapore_20240702.csv'
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
