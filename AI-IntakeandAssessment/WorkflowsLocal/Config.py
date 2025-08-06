from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class LLMConfig:
    """Configuration class for Azure OpenAI settings."""
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_OPENAI_MODEL_NAME = os.getenv('AZURE_OPENAI_MODEL_NAME')
    AZURE_OPENAI_TEMPERATURE = float(os.getenv('AZURE_OPENAI_TEMPERATURE', 0))
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
