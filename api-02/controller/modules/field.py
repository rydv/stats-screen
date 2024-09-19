import re
from abc import ABC, abstractmethod

class Field:
    def __init__(self, name, alias, value):
        self.name = name
        self.alias = alias
        self.value = value.strip() if value else None
        self.operations = self._parse_operations()

    def _parse_operations(self):
        if not self.value:
            return []

        operations = []
        operation_strings = self.value.split('||')

        for op_string in operation_strings:
            op_info = self._parse_single_operation(op_string)
            if op_info:
                operations.append(op_info)

        return operations

    def _parse_single_operation(self, op_string):
        op_info = {
            'id': None,
            'exp_flag': False,
            'valdt_flag': False,
            'op_flag': False,
            'perf_ref_flag': False,
            'fm_flag': False,
            'field_value_flag': False,
            'partname_flag': False,
            'ignore_patterns': [],
            'valdt_params': {},
            'op_params': {},
            'perf_ref_params': {},
            'field_value_params': {},
            'split_values': [],
            'search_agg_exp': None
        }

        id_match = re.match(r'\|ID\|(\d+)\|', op_string)
        if id_match:
            op_info['id'] = int(id_match.group(1))
            op_string = op_string[id_match.end():].strip()

        parts = re.split(r'(\|EXACT\||\|EXP\||\|FRMT\||\|OP\||\|PerfRef\||\|FM\||\|IGNORE\||\|PARTNAME\||\|FIELD_VALUE\|)', op_string)

        for i in range(0, len(parts), 2):
            identifier = parts[i]
            content = parts[i + 1] if i + 1 < len(parts) else ''

            strategy = self._get_strategy(identifier)
            if strategy:
                parsed_value = strategy.parse(content)
                self._update_op_info(op_info, identifier, parsed_value)

        op_info['search_agg_exp'] = self._create_search_agg_exp(op_info)

        return op_info

    def _create_search_agg_exp(self, op_info):
        if op_info['perf_ref_flag']:
            return ""

        parts = []
        for value in op_info['split_values']:
            if 'exact' in value:
                parts.append(re.escape(value['exact']))
            if 'exp' in value:
                parts.append(value['exp'])
            if 'partname' in value:
                parts.append(r'([A-Za-z\s]+)')
            if 'field_value' in value:
                parts.append(value['field_value']['exp'])

        expression = ''.join(parts)

        return expression

    def _get_strategy(self, identifier: str):
        if identifier == '|EXACT|':
            return ExactStrategy()
        elif identifier == '|EXP|':
            return ExpStrategy()
        elif identifier == '|FRMT|':
            return FRMTStrategy()
        elif identifier == '|OP|':
            return OpStrategy()
        elif identifier == '|PerfRef|':
            return PerfRefStrategy()
        elif identifier == '|FM|':
            return FMStrategy()
        elif identifier == '|IGNORE|':
            return IgnoreStrategy()
        elif identifier == '|PARTNAME|':
            return PartNameStrategy()
        elif identifier == '|FIELD_VALUE|':
            return FieldValueStrategy()
        else:
            return None

    def _update_op_info(self, op_info, identifier, parsed_value):
        if identifier == '|EXACT|':
            op_info['split_values'].append(parsed_value)
        elif identifier == '|EXP|':
            op_info['exp_flag'] = True
            op_info['split_values'].append(parsed_value)
        elif identifier == '|FRMT|':
            op_info['valdt_flag'] = True
            op_info['valdt_params'].update(parsed_value)
        elif identifier == '|OP|':
            op_info['op_flag'] = True
            op_info['op_params'].update(parsed_value)
        elif identifier == '|PerfRef|':
            op_info['perf_ref_flag'] = True
            op_info['perf_ref_params'].update(parsed_value)
        elif identifier == '|FM|':
            op_info['fm_flag'] = parsed_value['fm']
        elif identifier == '|IGNORE|':
            op_info['ignore_patterns'].append(parsed_value)
        elif identifier == '|PARTNAME|':
            op_info['partname_flag'] = True
            op_info['exp_flag'] = True
            op_info['split_values'].append(parsed_value)
        elif identifier == '|FIELD_VALUE|':
            op_info['field_value_flag'] = True
            op_info['exp_flag'] = True
            op_info['field_value_params'].update(parsed_value)
            op_info['split_values'].append(parsed_value)

class ExpressionStrategy(ABC):
    @abstractmethod
    def parse(self, content: str):
        pass

class ExactStrategy(ExpressionStrategy):
    def parse(self, content: str):
        return {'exact': content}

class ExpStrategy(ExpressionStrategy):
    def parse(self, content: str):
        return {'exp': content}

class FRMTStrategy(ExpressionStrategy):
    def parse(self, content: str):
        return {'date_format': date_format_mapping.get(content.strip(), content.strip())}

class OpStrategy(ExpressionStrategy):
    def parse(self, content: str):
        parts = content.strip().split('|')
        return {
            'op_type': parts[0],
            's1': parts[1],
            's2': parts[2] if len(parts) > 2 else ''
        }

class PerfRefStrategy(ExpressionStrategy):
    def parse(self, content: str):
        perf_ref_match = re.search(r'RL\|([0-9-]+)', content)
        result = {
            'min_length': None,
            'max_length': None,
            'exact_length': None
        }
        
        if perf_ref_match:
            rl_value = perf_ref_match.group(1)
            if '-' in rl_value:
                min_max = rl_value.split('-')
                if min_max[0]:
                    result['min_length'] = int(min_max[0])
                if min_max[1]:
                    result['max_length'] = int(min_max[1])
            elif rl_value:
                result['exact_length'] = int(rl_value)
        else:
            result['min_length'] = 5
        
        return result

class FMStrategy(ExpressionStrategy):
    def parse(self, content: str):
        if content.upper() == 'F':
            return {'fm': False}
        else:
            return {'fm': True}

class IgnoreStrategy(ExpressionStrategy):
    def parse(self, content: str):
        return content.strip()
    
class PartNameStrategy(ExpressionStrategy):
    def parse(self, content: str):
        return {'partname': True}
    
class FieldValueStrategy(ExpressionStrategy):
    def parse(self, content: str):
        field_name, exp = content.split('|')
        return {'field_value': {'field_name': field_name, 'exp': exp}}
