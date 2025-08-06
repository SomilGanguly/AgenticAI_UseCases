from langchain_openai import AzureChatOpenAI
from os import getenv

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

def main():
    llm = createOpenAIClient()

    print(llm.invoke('What is the capital of India?'))
