import os

selected_fields = [
    'AGENT_CODE', 'ACCT_CLASSIFICATION', 'SFIELD_8', 'SFIELD_9', 'C_OR_D', 'ITEM_ID',
    'LAST_ACTION_DATE', 'CLASS_DESCRIPTION', 'RELATIONSHIP_ID', 'PASS_NAME', 'SIDE_SORT',
    'USER_ID1'
]

root_path = '/opt/appl/aistore/portal/recon_pulse_mm'
matched_data_index = "manual_matched_data_singapore_testing"
reports_path = os.path.join(root_path, 'controllers/matching_matrix_controller/reports/')
input_path = os.path.join(root_path, 'controllers/matching_matrix_controller/files/')

date_format_mapping = {
    'DDMMYYYY': "%d%m%Y",
    'DD.MM.YY': '%d.%m.%y',
    'DD MON YYYY': '%d %b %Y'
}

configured_reports_index = "matching_matrix_configured_reports"
reports_run_index = 'matching_matrix_report_runs_index'
ARCHIVAL_DAYS = 4


amount_columns_mapping = {
    'amount_flag': 'AMOUNT',
    'amount1_flag': 'AMOUNT1',
}


col_mapping = {
    'ref1': 'SFIELD_7',
    'ref2': 'SFIELD_8',
    'ref3': 'SFIELD_9',
    'ref4': 'REFERENCE',
    'string1': 'STRING_1',
    'string2': 'STRING_2',
    'string3': 'STRING_3',
    'string4': 'STRING_4',
    'string5': 'STRING_5',
    'string6': 'STRING_6',
    'string7': 'STRING_7',
    'string8': 'STRING_8',
    'string9': 'STRING_9',
    'string10': 'STRING_10',
    'string11': 'STRING_11',
    'string12': 'STRING_12',
    'string13': 'STRING_13',
    'string14': 'STRING_14',
    'string15': 'STRING_15',
    'string16': 'STRING_16',
    'string17': 'STRING_17',
    'string18': 'STRING_18',
    'string19': 'STRING_19',
    'string20': 'STRING_20',
    'string21': 'STRING_21',
    'string22': 'STRING_22',
    'string23': 'STRING_23',
    'string24': 'STRING_24'
}
