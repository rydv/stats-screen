from pydantic import BaseModel, Field, validator
from typing import Dict

class RuleParams(BaseModel):
    unique_rule_id: str
    category_code: str
    set_id: str
    or_and_flag: str
    value_date_flag: str
    amount_flag: str
    ls_flag: str
    dc_flag: str
    amount_check_flags: Dict = Field(default_factory=dict)

    @validator('unique_rule_id', 'category_code', 'set_id', 'or_and_flag', 'value_date_flag', 'amount_flag', 'ls_flag', 'dc_flag', pre=True)
    def check_not_empty(cls, v):
        if not v:
            raise ValueError('Field cannot be empty')
        return v

    @validator('amount_check_flags')
    def check_dict_not_empty(cls, v):
        if not v:
            raise ValueError('amount_check_flags cannot be empty')
        return v
