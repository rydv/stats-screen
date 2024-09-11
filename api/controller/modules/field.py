import re

class Field:
    def __init__(self, name, alias, value):
        self.name = name
        self.alias = alias
        self.value = value.strip() if value else None
        self.identifiers_list = ['EXACT', 'EXP', 'FRMT', 'OP', 'PerfRef', 'FM', 'IGNORE', 'PARTNAME', 'FIELD_VALUE']

        # Initialize flags and parameters
        self.id = None
        self.exp_flag = False
        self.valdt_flag = False
        self.op_flag = False
        self.perf_ref_flag = False
        self.fm_flag = False
        self.field_value_flag = False
        self.partname_flag = False
        self.ignore_patterns = []

        self.valdt_params = {}
        self.op_params = {}
        self.perf_ref_params = {}
        self.field_value_params = {}

        # If a value is provided, process it
        if self.value:
            self._extract_id()  
            self.split_values = self._parse_value()
            self.search_agg_exp = self._create_search_agg_exp()
        else:
            self.split_values = None
            self.search_agg_exp = None

    def _extract_id(self):
        id_match = re.match(r'\|ID\|(\d+)\|', self.value)
        if id_match:
            self.id = int(id_match.group(1))
            self.value = self.value[id_match.end():].strip()

    def _parse_value(self):
        split_values = []
        pattern = '|'.join(f'(\\|{identifier}\\|)' for identifier in self.identifiers_list)
        parts = re.split(pattern, self.value)[1:]

        for i in range(0, len(parts), 2):
            identifier = parts[i]
            content = parts[i + 1] if i + 1 < len(parts) else ''

            strategy = self._get_strategy(identifier)
            parsed_value = strategy.parse(content)

            if identifier == '|EXACT|':
                split_values.append(parsed_value)
            elif identifier == '|EXP|':
                self.exp_flag = True
                split_values.append(parsed_value)
            elif identifier == '|FRMT|':
                self.valdt_flag = True
                self.valdt_params.update(parsed_value)
            elif identifier == '|OP|':
                self.op_flag = True
                self.op_params.update(parsed_value)
            elif identifier == '|PerfRef|':
                self.perf_ref_flag = True
                self.perf_ref_params.update(parsed_value)
            elif identifier == '|FM|':
                self.fm_flag = parsed_value['fm']
            elif identifier == '|IGNORE|':
                self.ignore_patterns.append(parsed_value)
            elif identifier == '|PARTNAME|':
                self.partname_flag = True
                self.exp_flag = True
                split_values.append(parsed_value)
            elif identifier == '|FIELD_VALUE|':
                self.field_value_flag = True
                self.exp_flag = True
                self.field_value_params.update(parsed_value)
                split_values.append(parsed_value)

        return split_values

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
            pass

    def _create_search_agg_exp(self):
        if self.perf_ref_flag:
            return ""

        parts = []
        for value in self.split_values:
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
        return {'op_details': content.strip()}

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
