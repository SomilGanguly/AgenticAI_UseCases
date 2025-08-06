from pydantic import BaseModel
from enum import Enum

class Status(Enum):
    intialized = 'initialized'
    running = 'running'
    completed = 'completed'
    failed = 'failed'

class ExecutionState(BaseModel):
    execution_id: str
    status: Status = Status.intialized  # Possible values: 'initialized', 'running', 'completed', 'failed'
    result: BaseModel | None = None  # Result can be any Pydantic model or None if not yet set
    error: str | None = None  # Error message if execution fails, otherwise None