# Documentation
This file contains all the library releated documentation.

## WorkFlow
WorkFlow is the chain of logical nodes. Each node responsible do a small task which contributes to overall work.

- #### WorkFlowBase
    WorkFlowBase is the Base class of any user defined workflow.<br><br>
    
    *Example of Workflow implementation :*
    ```python
    class TranscriptToAIF(WorkFlowBase):
        def func1(self, state: State):
            # Function Definition
            return state
        
        def func2(self, state: State):
            # Function Definition
            return state
        
        def buildGraph(self):
            self.getStateGraph().add_node("func1", self.func1)
            self.getStateGraph().add_node("func2", self.func2)

            self.getStateGraph().add_edge(self.getStartNodePointer(), "func1")
            self.getStateGraph().add_edge("func1", "func2")
            self.getStateGraph().add_edge("func2", self.getEndNodePointer())
    ```
    <br>

    *Example of Calling the WorkFlow*
    ```python
    from os import getenv
    from langchain_openai import AzureChatOpenAI
    from .WorkFlow import TranscriptToAIF

    llm = AzureChatOpenAI(
        deployment_name=getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        model_name=getenv('AZURE_OPENAI_MODEL_NAME'),
        temperature=float(getenv('AZURE_OPENAI_TEMPERATURE', 0.7)),
        api_key=getenv('AZURE_OPENAI_API_KEY'),
        azure_endpoint=getenv('AZURE_OPENAI_ENDPOINT'),
        api_version=getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    )

    workflow = TranscriptToAIF(llm)
    workflow.createStateGraph(State)
    workflow.buildGraph()
    
    input = State()

    result = workflow.invoke(input)
    print(result)
    ```