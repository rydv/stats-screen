import re

class ExpressionOperation:
    def __init__(self, field_name, content):
        self.field_name = field_name
        self.pattern = content

    def validate(self):
        try:
            re.compile(self.pattern)
            return True
        except re.error:
            return False

    def apply(self, data):
        return re.findall(self.pattern, data[self.field_name])

def create_expression_operations(rule):
    expression_ops = []
    for op in rule.operations:
        if op['op_type'] == '|EXP|':
            expression_ops.append(ExpressionOperation(op['field_name'], op['content']))
    return expression_ops
