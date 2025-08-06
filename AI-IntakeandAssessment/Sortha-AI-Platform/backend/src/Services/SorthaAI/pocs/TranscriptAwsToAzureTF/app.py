from os import getenv

from langchain_openai import AzureChatOpenAI
from .WorkFlow import TranscriptToAIF
from .State import State
from .TerraformCodeParser import TerraformCodeParser
from .FileWriterAgent import FileWriterAgent

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

    with open('C:\\Users\\rohanverma\\OneDrive - Microsoft\\Desktop\\dev\\Infra and Sec COE\\sortha\\.dontCommit\\outputs\\raw_output.txt', 'w', encoding='utf-8') as file:
        file.write(str(result))

    # tf_parser = TerraformCodeParser(dict(result)['terraform_resources'])
    # tf_parser.compile()
    # with open('C:\\Users\\rohanverma\\OneDrive - Microsoft\\Desktop\\dev\\Infra and Sec COE\\sortha\\.dontCommit\\outputs\\main.tf', 'w', encoding='utf-8') as file:
    #     file.write(tf_parser.getCodeString())

    fa = FileWriterAgent('C:\\Users\\rohanverma\\OneDrive - Microsoft\\Desktop\\dev\\Infra and Sec COE\\sortha\\.dontCommit\\outputs\\home')
    fa.writeFile(dict(result)['terraform_code'])

    print(result)