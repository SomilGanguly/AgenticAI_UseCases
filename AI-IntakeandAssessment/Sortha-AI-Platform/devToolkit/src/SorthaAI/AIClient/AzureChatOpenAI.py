from langchain_openai import AzureChatOpenAI as AIClient

class AzureChatOpenAI(AIClient):
    """
    Custom AzureChatOpenAI client that extends the base AIClient.
    This class can be used to add additional methods or properties specific to SorthaAI's requirements.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Additional initialization can be done here if needed