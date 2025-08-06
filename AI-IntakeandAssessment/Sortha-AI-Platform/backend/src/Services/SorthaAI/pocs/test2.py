from os import getenv
from typing import TypedDict
import random

from langchain_openai import AzureChatOpenAI

from WorkFlow.WorkFlowBase import WorkFlowBase


def createOpenAIClient():
    return AzureChatOpenAI(
        deployment_name=getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        model_name=getenv('AZURE_OPENAI_MODEL_NAME'),
        # temperature=float(getenv('AZURE_OPENAI_TEMPERATURE', 0.7)),
        temperature=0.7,
        api_key=getenv('AZURE_OPENAI_API_KEY'),
        azure_endpoint=getenv('AZURE_OPENAI_ENDPOINT'),
        api_version=getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    )


class State(TypedDict):
    question: str
    answer: str
    isTrue: bool
    sayLie: bool


class TestWorkflow(WorkFlowBase):
    def SayTruthOrLie(self, state: State):
        if random.randint(0, 1) == 0:
            return {"sayLie": False}
        else:
            return {"sayLie": True}

    def CreateAnswer(self, state: State):
        ans = ''
        if state['sayLie']:
            ans = self.getLLM().invoke(
                f'Answer the question with justification in a way that it is factually incorrect and sounds funny: {state["question"]}')
        else:
            ans = self.getLLM().invoke(
                f'Answer the question with justification in a way that it is factually: {state["question"]}')
        state['answer'] = ans.content
        return state

    def CheckAnswer(self, state: State):
        structuredLLM = self.getLLM().with_structured_output({
            "title": "checkAnswer",
            "description": "Check if the answer is true or false",
            "type": "object",
            "properties": {
                "isTrue": {
                    "type": "boolean",
                    "description": "Is the answer true"
                }
            }
        })

        state["isTrue"]=structuredLLM.invoke(
            f'Is the following answer true or false? {state["answer"]}'
        )['isTrue']

        return state
    
    def buildGraph(self):
        self.getStateGraph().add_node("SayTruthOrLie", self.SayTruthOrLie)
        self.getStateGraph().add_node("CreateAnswer", self.CreateAnswer)
        self.getStateGraph().add_node("CheckAnswer", self.CheckAnswer)

        self.getStateGraph().add_edge(self.getStartNodePointer(), "SayTruthOrLie")
        self.getStateGraph().add_edge("SayTruthOrLie", "CreateAnswer")
        self.getStateGraph().add_edge("CreateAnswer", "CheckAnswer")
        self.getStateGraph().add_edge("CheckAnswer", self.getEndNodePointer())


def main():
    llm = createOpenAIClient()
    workflow = TestWorkflow(llm)
    workflow.createStateGraph(State)
    workflow.buildGraph()

    s = State(question='Where does Apples come from?')
    print(workflow.invoke(s))
