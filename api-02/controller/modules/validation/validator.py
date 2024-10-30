from typing import Dict, List, Tuple
import pandas as pd
import os
import re

# Constants
VALID_VALUE_DATE_FLAGS = ['ALL', 'ANY', 'S', 'SAME', 'A', 'D', 'DIFFERENT']
VALID_AMOUNT_FLAGS = ['ALL', 'ANY', 'S', 'SAME', 'A', 'D', 'DIFFERENT']
AMOUNT_PATTERN = r'^(\|)?(DIFFERENT|D)\|(LE|L|G|GE)\|-?\d+\.?\d*(\|)?'
VALID_OR_AND_FLAGS = ['AND', 'OR']
VALID_LS_FLAGS = ['L', 'S', 'A', 'ANY', 'ALL']
VALID_DC_FLAGS = ['D', 'C', 'A', 'ANY', 'ALL', 'D WO', 'C WO']

class RuleSheetValidator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.validated_groups = []
        
    def validate(self) -> Tuple[bool, Dict]:
        try:
            df = self._read_excel()
            if df is None:
                return False, self._format_response()

            df = self._clean_data(df)
            
            if not self._validate_headers(df):
                return False, self._format_response()
                
            df = self._process_rules(df)
            
            if len(self.errors) == 0 and df is not None:
                self._save_validated_file(df)
            
            return len(self.errors) == 0, self._format_response()
            
        except Exception as e:
            self.errors.append(f"Unexpected error: {str(e)}")
            return False, self._format_response()

    def _read_excel(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.file_path, sheet_name='RULE SHEET')
            return df
        except Exception as e:
            self.errors.append(f"Failed to read Excel file: {str(e)}")
            return None

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all', axis=0)
        return df

    def _validate_headers(self, df: pd.DataFrame) -> bool:
        missing_headers = set(REQUIRED_HEADERS) - set(df.columns)
        if missing_headers:
            self.errors.append(f"Missing required headers: {', '.join(missing_headers)}")
            return False
            
        if not any(header in df.columns for header in REF_HEADERS):
            self.errors.append("At least one reference or string column is required")
            return False
            
        return True

    def _process_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        df['unique_rule_id'] = df['unique_rule_id'].fillna(method='ffill')
        
        for rule_id, group in df.groupby('unique_rule_id'):
            validated_group_category_code = self._validate_category_code(rule_id, group)
            
            validated_group_set_id = self._validate_set_id(
                rule_id, 
                validated_group_category_code if validated_group_category_code is not None else group
            )
            
            validated_group_value_date = self._validate_value_date_flag(
                rule_id, 
                validated_group_set_id if validated_group_set_id is not None else group
            )
            
            validated_group_amount = group
            for col in group.columns:
                if col.startswith('amount') and col.endswith('_flag'):
                    validated_group_amount = self._validate_amount_flag(
                        rule_id,
                        validated_group_amount if validated_group_amount is not None else group,
                        col
                    )
            
            validated_group_or_and = self._validate_or_and_flag(
                rule_id, 
                validated_group_amount if validated_group_amount is not None else group
            )

            validated_group_ls_flag = self._validate_ls_flag(
                rule_id,
                validated_group_or_and if validated_group_or_and is not None else group
            )

            validated_group_dc_flag = self._validate_dc_flag(
                rule_id,
                validated_group_ls_flag if validated_group_ls_flag is not None else group
            )

            if all(v is not None for v in [
                validated_group_category_code,
                validated_group_set_id,
                validated_group_value_date,
                validated_group_amount,
                validated_group_or_and,
                validated_group_ls_flag,
                validated_group_dc_flag
            ]):
                self.validated_groups.append(validated_group_dc_flag)
        
        if self.validated_groups:
            return pd.concat(self.validated_groups, ignore_index=True)
        return None

    def _validate_category_code(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        if group is None:
            return None
            
        unique_categories = group['category_code'].dropna().unique()
        unique_categories = [str(cat).strip().upper() for cat in unique_categories]
        
        if len(unique_categories) > 1:
            self.errors.append(f"Rule {rule_id}: Multiple category codes found: {', '.join(unique_categories)}")
            return None
            
        if unique_categories:
            category = unique_categories[0]
            if ',' in category:
                self.errors.append(f"Rule {rule_id}: Category code contains invalid character ','")
                return None
            if category.upper() in INVALID_CATEGORY_VALUES:
                self.errors.append(f"Rule {rule_id}: Invalid category code '{category}'")
                return None
                
            group['category_code'] = group['category_code'].apply(lambda x: category if pd.isna(x) or str(x).strip() == '' else x)
            
        return group
    
    def _validate_set_id(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        if group is None:
            return None
            
        unique_set_ids = group['set_id'].dropna().unique()
        unique_set_ids = [str(set_id).strip().upper() for set_id in unique_set_ids]        
        if len(unique_set_ids) > 1:
            self.errors.append(f"Rule {rule_id}: Multiple set IDs found: {', '.join(unique_set_ids)}")
            return None
            
        if unique_set_ids:
            set_id = unique_set_ids[0]
            group['set_id'] = group['set_id'].apply(lambda x: set_id if pd.isna(x) or str(x).strip() == '' else x)
            
        return group

    def _validate_value_date_flag(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        if group is None:
            return None
            
        unique_flags = group['value_date_flag'].dropna().unique()
        unique_flags = [str(flag).strip().upper() for flag in unique_flags]
        
        if len(unique_flags) > 1:
            self.errors.append(f"Rule {rule_id}: Multiple value date flags found: {', '.join(unique_flags)}")
            return None
            
        if unique_flags:
            flag = unique_flags[0]
            if flag not in VALID_VALUE_DATE_FLAGS:
                self.errors.append(f"Rule {rule_id}: Invalid value date flag '{flag}'")
                return None
                
            group['value_date_flag'] = group['value_date_flag'].apply(
                lambda x: flag if pd.isna(x) or str(x).strip() == '' else x
            )
            
        return group

    def _validate_amount_flag(self, rule_id: str, group: pd.DataFrame, flag_column: str = 'amount_flag') -> pd.DataFrame:
        if group is None:
            return None
            
        unique_flags = group[flag_column].dropna().unique()
        unique_flags = [str(flag).strip().upper() for flag in unique_flags]
        
        if len(unique_flags) > 1:
            self.errors.append(f"Rule {rule_id}: Multiple amount flags found in {flag_column}: {', '.join(unique_flags)}")
            return None
            
        if unique_flags:
            flag = unique_flags[0]
            if flag not in VALID_AMOUNT_FLAGS and not re.match(AMOUNT_PATTERN, flag):
                self.errors.append(f"Rule {rule_id}: Invalid amount flag '{flag}' in {flag_column}")
                return None
                
            group[flag_column] = group[flag_column].apply(
                lambda x: flag if pd.isna(x) or str(x).strip() == '' else x
            )
            
        return group
    
    def _validate_or_and_flag(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        if group is None:
            return None
            
        unique_flags = group['or_and_flag'].dropna().unique()
        unique_flags = [str(flag).strip().upper() for flag in unique_flags]
        
        if len(unique_flags) > 1:
            self.errors.append(f"Rule {rule_id}: Multiple OR/AND flags found: {', '.join(unique_flags)}")
            return None
            
        if unique_flags:
            flag = unique_flags[0]
            if flag not in VALID_OR_AND_FLAGS:
                self.errors.append(f"Rule {rule_id}: Invalid OR/AND flag '{flag}'")
                return None
                
            group['or_and_flag'] = group['or_and_flag'].apply(
                lambda x: flag if pd.isna(x) or str(x).strip() == '' else x
            )
            
        return group
    
    def _validate_ls_flag(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        if group is None:
            return None
            
        ls_flags = group['ls_flag'].fillna('')
        ls_flags = [str(flag).strip().upper() for flag in ls_flags]
        
        if '' in ls_flags:
            self.errors.append(f"Rule {rule_id}: Empty ls_flag values found")
            return None
            
        invalid_flags = [flag for flag in ls_flags if flag not in VALID_LS_FLAGS]
        if invalid_flags:
            self.errors.append(f"Rule {rule_id}: Invalid ls_flag values found: {', '.join(invalid_flags)}")
            return None
                
        return group

    def _validate_dc_flag(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        if group is None:
            return None
            
        dc_flags = group['dc_flag'].fillna('')
        dc_flags = [str(flag).strip().upper() for flag in dc_flags]
        
        if '' in dc_flags:
            self.errors.append(f"Rule {rule_id}: Empty dc_flag values found")
            return None
            
        invalid_flags = [flag for flag in dc_flags if flag not in VALID_DC_FLAGS]
        if invalid_flags:
            self.errors.append(f"Rule {rule_id}: Invalid dc_flag values found: {', '.join(invalid_flags)}")
            return None
                
        return group

    def _save_validated_file(self, df: pd.DataFrame):
        validated_file_path = self.file_path.replace('_temp', '_validated')
        df.to_excel(validated_file_path, sheet_name='RULE SHEET', index=False)

    def _format_response(self) -> Dict:
        return {
            'errors': self.errors,
            'warnings': self.warnings
        }