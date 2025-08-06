import json
from pydantic import BaseModel
from typing import Any
from langgraph.pregel.io import AddableValuesDict

def serialize_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.dict()
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    else:
        return value
    
def addable_values_dict_to_json(avd: AddableValuesDict) -> str:
    serialized = {k: serialize_value(v) for k, v in avd.items()}
    return json.dumps(serialized, indent=4)
