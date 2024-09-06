from pydantic import BaseModel, Field, validator
from typing import Dict

class RuleParams(BaseModel):
    unique_rule_id: str
    category_code: str
    set_id: str
    amount: str
    value_date: str

    @validator('unique_rule_id', 'category_code', 'set_id', 'amount', 'value_date')
    def not_empty(cls, v):
        if not v:
            raise ValueError('Field cannot be empty')
        return v