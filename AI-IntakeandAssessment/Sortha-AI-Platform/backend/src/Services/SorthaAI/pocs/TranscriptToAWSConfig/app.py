from os import getenv

from langchain_openai import AzureChatOpenAI
from .WorkFlow import TranscriptToAIF
from .State import State

def createOpenAIClient():
    return AzureChatOpenAI(
        deployment_name=getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        model_name=getenv('AZURE_OPENAI_MODEL_NAME'),
        temperature=float(getenv('AZURE_OPENAI_TEMPERATURE', 0.7)),
        api_key=getenv('AZURE_OPENAI_API_KEY'),
        azure_endpoint=getenv('AZURE_OPENAI_ENDPOINT'),
        api_version=getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    )


def main():
    llm = createOpenAIClient()
    workflow = TranscriptToAIF(llm)
    workflow.createStateGraph(State)
    workflow.buildGraph()
    
    input = State(
        transcript={
            'source_path': 'C:\\Users\\rohanverma\\OneDrive - Microsoft\\Desktop\\dev\\Infra and Sec COE\\sortha\\.dontCommit\\inputs\\rohanRohonTranscriptTest.txt'
        },
        retry_limit=5
    )

    result = workflow.invoke(input)
    print(result)