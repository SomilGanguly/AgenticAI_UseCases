from dotenv import load_dotenv
load_dotenv('C:\\Users\\rohanverma\\OneDrive - Microsoft\\Desktop\\dev\\Infra and Sec COE\\sortha-paas\\devToolkit\\.dontCommit\\userTestCode\\.env')
from os import getenv

class LLMConfig:
    AZURE_OPENAI_DEPLOYMENT_NAME = getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_OPENAI_MODEL_NAME = getenv('AZURE_OPENAI_MODEL_NAME')
    AZURE_OPENAI_TEMPERATURE = float(getenv('AZURE_OPENAI_TEMPERATURE', 0))
    AZURE_OPENAI_API_KEY = getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')

class InputConfig:
    inputs = {
        'transcript': {
            'description': 'The Transcript file to be processed',
            'type': 'file'
        },
        'retry_limit': {
            'description': 'Number of times to retry the workflow in case of failure',
            'type': 'number',
        }
    }
    metadata = {
        'name': 'Transcript to AIF',
        'description': 'Converts a transcript to an AIF file'
    }