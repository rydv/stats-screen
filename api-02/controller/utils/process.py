import pandas as pd
import traceback
from typing import List, Dict
from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.rule_builder import RuleBuilder
from controllers.matching_matrix_controller.modules.rule import Rule

def build_rule(rule_id: str, group: pd.DataFrame) -> Rule:
    rule_builder = RuleBuilder()
    
    first_row = group.iloc[0]
    rule_params = RuleParams(
        unique_rule_id=rule_id,
        category_code=first_row['category_code'],
        set_id=first_row['set_id'],
        amount_check_flags={flag: first_row[flag] for flag in amount_columns_mapping.keys() if first_row[flag]},
        value_date_flag=first_row['value_date_flag'],
        or_and_flag=first_row['or_and_flag'],
    )
    rule_builder.set_params(rule_params)

    for _, row in group.iterrows():
        l_s = row['ls_flag']
        d_c = row['dc_flag']
        reffields = list(set(row.keys()) & set(col_mapping.keys()))
        fields = [Field(col_mapping[col], col, row[col]) for col in reffields]
        rule_builder.add_filter(l_s, d_c, fields)

    return rule_builder.build()

def process_rules(file: Dict) -> Dict:
    try:
        inp_file_name = file['_source']['uploadedFileName']
        file_path = os.path.join(input_path, inp_file_name)
        print(file_path)

        if not os.path.isfile(file_path):
            return {
                'status': False, 
                'output': None, 
                'error_details': f'File does not exist: {file_path}'
            }

        csv_data = pd.read_csv(file_path).fillna("")
        rules_to_process = []

        for rule_id, group in csv_data.groupby('unique_rule_id'):
            try:
                rule = build_rule(rule_id, group)
                rules_to_process.append(rule)
            except Exception as e:
                print(f"Failed to build rule {rule_id}: {str(e)}")
                continue

        rule_matches = []
        matches_df = pd.DataFrame()

        print("Processing rules...")
        for rule in rules_to_process:
            print(f"Rule: {rule.rule_params.unique_rule_id}")
            matches_df = rule.find_matches()
            if len(matches_df):
                rule_matches.append(matches_df)

        if len(rule_matches):
            print("Aggregating matches")
            res_df = pd.concat(rule_matches)
            res_df.reset_index(drop=False, inplace=True)
            res_df.sort_values(by='RELATIONSHIP_ID', inplace=True)
            res_df.drop_duplicates(subset='ITEM_ID', keep='first', inplace=True)
            
            report_path = os.path.join(reports_path, 'manual_rule_analysis_report_singapore_20240702.csv')
            res_df.to_csv(report_path, index=False)
            
            run_summary = res_df['Rule_Id'].value_counts().to_dict()
            run_summary = {k: int(v) for k, v in run_summary.items()}
        else:
            print("Nothing to concat.")
            res_df = pd.DataFrame()
            run_summary = {}

        return {
            'status': True,
            'output': {
                "matches": res_df,
                'valid_rules': rules_to_process,
                "run_summary": {
                    "matches": f"{len(run_summary)}/{len(rules_to_process)}",
                    "matches_count": run_summary,
                }
            },
            'error_details': None
        }

    except Exception as e:
        error_msg = f'Failed to process rules due to error: {str(e)}'
        print(error_msg)
        print(traceback.format_exc())
        return {
            'status': False,
            'output': None,
            'error_details': error_msg
        }
