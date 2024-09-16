from rule import Rule
from filter import Filter

class RuleBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._rule_params = None
        self._filters = []

    def set_params(self, rule_params):
        self._rule_params = rule_params
        return self

    def add_filter(self, fields):
        new_filter = Filter(fields)
        self._filters.append(new_filter)
        return self

    def build(self):
        if not self._rule_params:
            raise ValueError("Rule parameters are not set")
        if not self._filters:
            raise ValueError("No filters added to the rule")
        
        rule = Rule(self._rule_params, self._filters)
        self.reset()
        return rule
