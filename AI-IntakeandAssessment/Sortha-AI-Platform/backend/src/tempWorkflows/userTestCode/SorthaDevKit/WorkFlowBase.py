from abc import ABC, abstractmethod


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