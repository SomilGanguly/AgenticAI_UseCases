def getStateBaseContent() -> str:
    return '''from pydantic import BaseModel, Field
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
'''

def getWorkFlowBaseContent() -> str:
    return '''from abc import ABC, abstractmethod


from langgraph.graph import StateGraph, START, END
from langchain_core.language_models.chat_models import BaseChatModel

class WorkFlowBase(ABC):
    def __init__(self, llm: BaseChatModel) -> None:
        self.__llm = llm
        self.__stateGraph = None

    def createStateGraph(self, state) -> None:
        if self.__stateGraph is None:
            self.__stateGraph = StateGraph(state)
        else:
            raise ValueError("Workflow has already been initialized. Use a different state or create a new instance.")
    
    def getStateGraph(self) -> StateGraph:
        if self.__stateGraph is not None:
            return self.__stateGraph
        else:
            raise ValueError("Workflow has not been initialized. Call createStateGraph first.")

    def getStartNodePointer(self) -> str:
        return START
    
    def getEndNodePointer(self) -> str:
        return END
    
    def getLLM(self) -> BaseChatModel:
        return self.__llm

    @abstractmethod
    def buildGraph(self) -> None:
        pass

    def invoke(self, state) -> str:
        if self.__stateGraph is None:
            raise ValueError("Workflow has not been initialized. Call createStateGraph first.")
        return self.__stateGraph.compile().invoke(state)
'''

def getEnvContent() -> str:
    return '''AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_MODEL_NAME=
AZURE_OPENAI_TEMPERATURE=0
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2025-01-01-preview
'''

def getConfigContent(cwd: str) -> str:
    return f'''from dotenv import load_dotenv
load_dotenv(\''''+cwd.replace('\\', '\\\\')+'''\\\\.env\')
from os import getenv

class LLMConfig:
    AZURE_OPENAI_DEPLOYMENT_NAME = getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_OPENAI_MODEL_NAME = getenv('AZURE_OPENAI_MODEL_NAME')
    AZURE_OPENAI_TEMPERATURE = float(getenv('AZURE_OPENAI_TEMPERATURE', 0))
    AZURE_OPENAI_API_KEY = getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')

# Dont worry about the code below. Ignore it. It will be used in the future versions of the SorthaDevKit.
class InputConfig:
    fileInputs = {
        'transcript': {
            'description': 'Path to the transcript file',
            'type': 'text'
        }
    }
    fieldInputs = {
        'retry_limit': {
            'description': 'Number of times to retry the workflow in case of failure',
            'type': 'number',
            'default': 5
        }
    }
'''

def getInputContent() -> str:
    return '''from StateBase import FileInputType, FileTypes

Input = {
    "variable_name": FileInputType(
        file_path="<absolute_path_to_file>",
        type=FileTypes.TEXT
    )
}
'''

def getStateContent() -> str:
    return '''from pydantic import BaseModel, Field
from StateBase import StateBase

class State(StateBase):
    retry_count: int = 0
    retry_limit: int = 3
'''

def getWorkFlowContent() -> str:
    return '''from WorkFlowBase import WorkFlowBase
from State import State

class CustomWorkFlow(WorkFlowBase):
    def fun1(self, state: State):
        return state
    
    def fun2(self, state: State):
        return state
    
    def formatedOutput(self, state: State):
        state.output = self.getLLM().invoke(f'Hello there!').content
        return state

    def buildGraph(self):
        self.getStateGraph().add_node("fun1", self.fun1)
        self.getStateGraph().add_node("fun2", self.fun2)
        self.getStateGraph().add_node("formatedOutput", self.formatedOutput)

        self.getStateGraph().add_edge(self.getStartNodePointer(), "fun1")
        self.getStateGraph().add_edge("fun1", "fun2")
        self.getStateGraph().add_edge("fun2", "formatedOutput")
        self.getStateGraph().add_edge("formatedOutput", self.getEndNodePointer())
'''


