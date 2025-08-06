from pydantic import BaseModel, Field
from typing import Union
from enum import Enum

class FileTypes(Enum):
    TEXT = 'text'
    EXCEL = 'excel'
    UNDEFINED = 'undefined'

class FileInputType(BaseModel):
    type: FileTypes = Field(default=FileTypes.UNDEFINED, description="Type of input, e.g. 'text', 'file', etc.")
    file_id: int = Field(default=0, description="ID of the file if the input is a file, otherwise None")
    content: str = Field(default='', description="Content of the input, e.g. text or file content")

class UserInputType(BaseModel):
    content: str = Field(default='', description="Content of the input, e.g. text or file content")


class StateBase(BaseModel):
    inputs: dict[str, Union[FileInputType, UserInputType]] = Field(default={}, description="Dictionary of inputs")
    output: str = Field(default='', description="Output of the workflow")