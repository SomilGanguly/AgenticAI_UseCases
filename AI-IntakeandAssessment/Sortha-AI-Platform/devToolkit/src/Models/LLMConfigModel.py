from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    AZURE_OPENAI_DEPLOYMENT_NAME = Field(description="Deployment name for Azure OpenAI")
    AZURE_OPENAI_MODEL_NAME = Field(description="Model name for Azure OpenAI")
    AZURE_OPENAI_TEMPERATURE = Field(default=0, description="Temperature setting for Azure OpenAI, default is 0")
    AZURE_OPENAI_API_KEY = Field(description="API key for Azure OpenAI")
    AZURE_OPENAI_ENDPOINT = Field(description="Endpoint for Azure OpenAI")
    AZURE_OPENAI_API_VERSION = Field(default='2025-01-01-preview', description="API version for Azure OpenAI, default is '2025-01-01-preview'")