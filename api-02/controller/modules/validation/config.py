# validation/config.py
REQUIRED_HEADERS = [
    'unique_rule_id', 'category_code', 'set_id', 'or_and_flag', 
    'value_date_flag', 'amount_flag', 'ls_flag', 'dc_flag'
]

REF_HEADERS = [f'ref{i}' for i in range(1, 5)] + [f'string{i}' for i in range(1, 51)]

INVALID_CATEGORY_VALUES = ['A', 'ALL', 'ANY']