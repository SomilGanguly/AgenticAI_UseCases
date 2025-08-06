from SorthaAI.AIClient.AzureChatOpenAI import AzureChatOpenAI

def createOpenAIClient(AZURE_OPENAI_DEPLOYMENT_NAME=None, AZURE_OPENAI_MODEL_NAME=None, AZURE_OPENAI_TEMPERATURE=0, AZURE_OPENAI_API_KEY=None, AZURE_OPENAI_ENDPOINT=None, AZURE_OPENAI_API_VERSION='2025-01-01-preview'):
    if AZURE_OPENAI_DEPLOYMENT_NAME==None:
        raise ValueError("'AZURE_OPENAI_DEPLOYMENT_NAME' is not set.")
    if AZURE_OPENAI_MODEL_NAME==None:
        raise ValueError("'AZURE_OPENAI_MODEL_NAME' is not set.")
    if AZURE_OPENAI_TEMPERATURE==None:
        raise ValueError("'AZURE_OPENAI_TEMPERATURE' is not set. Defaulting to 0.")
    if AZURE_OPENAI_API_KEY==None:
        raise ValueError("'AZURE_OPENAI_API_KEY' is not set.")
    if AZURE_OPENAI_ENDPOINT==None:
        raise ValueError("'AZURE_OPENAI_ENDPOINT' is not set.")
    if AZURE_OPENAI_API_VERSION==None:
        raise ValueError("'AZURE_OPENAI_API_VERSION' is not set. Defaulting to '2025-01-01-preview'.")
    
    return AzureChatOpenAI(
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        model_name=AZURE_OPENAI_MODEL_NAME,
        temperature=AZURE_OPENAI_TEMPERATURE,
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION
    )