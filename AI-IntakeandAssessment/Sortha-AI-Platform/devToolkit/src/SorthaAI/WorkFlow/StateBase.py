from pydantic import BaseModel, Field
from typing import Union, Iterator, Hashable
from enum import Enum
from pandas import Series

class FileTypes(Enum):
    TEXT = 'text'
    EXCEL = 'excel'
    UNDEFINED = 'undefined'

class FileInputType(BaseModel):
    type: FileTypes = Field(default=FileTypes.UNDEFINED, description="Type of input, e.g. 'text', 'file', etc.")
    file_path: str = Field(default='', description="Path to the file input")
    content: Union[str, Iterator[tuple[Hashable, Series]]] = Field(default='', description="Content of the input, e.g. text or file content")
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class UserInputType(BaseModel):
    content: str = Field(default='', description="Content of the input, e.g. text or file content")


class StateBase(BaseModel):
    inputs: dict[str, Union[FileInputType, UserInputType]] = Field(default={}, description="Dictionary of inputs")
    output: str = Field(default='', description="Output of the workflow")