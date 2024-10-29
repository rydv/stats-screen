from typing import Dict, List, Tuple
import pandas as pd

class RuleSheetValidator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        
    def validate(self) -> Tuple[bool, Dict]:
        try:
            # Read Excel file
            df = self._read_excel()
            if df is None:
                return False, self._format_response()

            # Clean data
            df = self._clean_data(df)
            
            # Validate headers
            if not self._validate_headers(df):
                return False, self._format_response()
                
            # Fill empty cells and validate rules
            df = self._process_rules(df)
            
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
        # Remove empty rows and columns
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        return df

    def _validate_headers(self, df: pd.DataFrame) -> bool:
        # Check required headers
        missing_headers = set(REQUIRED_HEADERS) - set(df.columns)
        if missing_headers:
            self.errors.append(f"Missing required headers: {', '.join(missing_headers)}")
            return False
            
        # Check reference headers
        if not any(header in df.columns for header in REFERENCE_HEADERS + STRING_HEADERS):
            self.errors.append("At least one reference or string column is required")
            return False
            
        return True

    def _process_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        # Fill empty unique_rule_id cells
        df['unique_rule_id'] = df['unique_rule_id'].fillna(method='ffill')
        
        # Process each rule group
        for rule_id, group in df.groupby('unique_rule_id'):
            self._validate_category_code(rule_id, group)
            
        return df

    def _validate_category_code(self, rule_id: str, group: pd.DataFrame):
        # Get unique non-null category codes
        unique_categories = group['category_code'].dropna().unique()
        unique_categories = [str(cat).strip() for cat in unique_categories]
        
        if len(unique_categories) > 1:
            self.errors.append(f"Rule {rule_id}: Multiple category codes found: {', '.join(unique_categories)}")
            
        if unique_categories:
            category = unique_categories[0]
            if ',' in category:
                self.errors.append(f"Rule {rule_id}: Category code contains invalid character ','")
            if category.upper() in INVALID_CATEGORY_VALUES:
                self.errors.append(f"Rule {rule_id}: Invalid category code '{category}'")

    def _format_response(self) -> Dict:
        return {
            'errors': self.errors,
            'warnings': self.warnings
        }