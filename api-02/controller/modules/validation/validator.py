from typing import Dict, List, Tuple
import pandas as pd
import os

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
        df = df.dropna(how='all', axis=1)
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
            validated_group = self._validate_category_code(rule_id, group)
            if validated_group is not None:
                # Add more validation methods here
                # validated_group = self._validate_next_field(rule_id, validated_group)
                self.validated_groups.append(validated_group)
        
        if self.validated_groups:
            return pd.concat(self.validated_groups, ignore_index=True)
        return None

    def _validate_category_code(self, rule_id: str, group: pd.DataFrame) -> pd.DataFrame:
        unique_categories = group['category_code'].dropna().unique()
        unique_categories = [str(cat).strip() for cat in unique_categories]
        
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
                
            # Fill empty category code cells and empty strings with the valid category
            group['category_code'] = group['category_code'].apply(lambda x: category if pd.isna(x) or str(x).strip() == '' else x)
            
        return group

    def _save_validated_file(self, df: pd.DataFrame):
        validated_file_path = self.file_path.replace('_temp', '_validated')
        df.to_excel(validated_file_path, sheet_name='RULE SHEET', index=False)

    def _format_response(self) -> Dict:
        return {
            'errors': self.errors,
            'warnings': self.warnings
        }
