from rule import Rule
from filter import Filter
from itertools import count

class RuleBuilder:
    def __init__(self):
        self.reset()
        self._id_counter = count(1)

    def reset(self):
        self._rule_params = None
        self._filters = []
        self._op_mapping = {}

    def set_params(self, rule_params):
        self._rule_params = rule_params
        return self

    def add_filter(self, l_s, d_c, fields):
        new_filter = Filter(l_s, d_c, fields)
        self._filters.append(new_filter)
        return self

    def _generate_op_mapping(self):
        for filter_index, filter in enumerate(self._filters):
            filter_key = f'filter-{filter_index + 1}'
            for field in filter.fields:
                for operation in field.operations:
                    op_type = self._determine_op_type(operation)
                    op_id = operation.get('id')
                    
                    if op_id is None:
                        op_id = self._find_or_create_custom_id(op_type)
                    
                    if op_id not in self._op_mapping:
                        self._op_mapping[op_id] = {
                            'op_type': op_type,
                            'filters': {}
                        }
                    
                    if filter_key not in self._op_mapping[op_id]['filters']:
                        self._op_mapping[op_id]['filters'][filter_key] = {
                            'ls_flag': filter.l_s,
                            'dc_flag': filter.d_c,
                            'fields': []
                        }
                    
                    self._op_mapping[op_id]['filters'][filter_key]['fields'].append(field)

    def _find_or_create_custom_id(self, op_type):
        for existing_id, op_info in self._op_mapping.items():
            if existing_id.startswith('custom_') and op_info['op_type'] == op_type:
                return existing_id
        return f'custom_{next(self._id_counter)}'

    def _determine_op_type(self, operation):
        if operation['exp_flag']:
            return 'expression_st'
        elif operation['valdt_flag']:
            return 'value_date_st'
        elif operation['perf_ref_flag']:
            return 'perf_ref_st'
        elif operation['partname_flag']:
            return 'client_name_st'
        elif operation['field_value_flag']:
            return 'field_value_st'
        else:
            return 'unknown_st'

    def build(self):
        if not self._rule_params:
            raise ValueError("Rule parameters are not set")
        if not self._filters:
            raise ValueError("No filters added to the rule")
        
        self._generate_op_mapping()
        rule = Rule(self._rule_params, self._filters, self._op_mapping)
        self.reset()
        return rule
