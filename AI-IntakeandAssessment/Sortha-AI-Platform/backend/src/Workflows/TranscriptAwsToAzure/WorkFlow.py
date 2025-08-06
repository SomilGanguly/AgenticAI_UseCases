from src.Services.SorthaAI.WorkFlow.WorkFlowBase import WorkFlowBase
from .State import State, Resources, YesOrNo

class TranscriptToAIF(WorkFlowBase):
    def loadTranscript(self, state: State):
        state.transcript = state.inputs['transcript_file'].content
        return state
    
    def extractResourceInformation(self, state: State):
        structuredLLM = self.getLLM().with_structured_output(Resources)
        state.aws_resources = structuredLLM.invoke(f'Provided following is the transcript generated after conversing with the customer. Analyse the conversation and predict the aws resouce configuration for the application: {state.transcript}').resources
        state.retry_count += 1
        return state
    
    def retryValidator(self, state: State):
        if state.retry_count >= state.retry_limit:
            print('Retry limit reached. Exiting workflow.')
            return 'PASS'
        
        structuredLLM = self.getLLM().with_structured_output(YesOrNo)
        response = structuredLLM.invoke(f'A conversation happend between the customer and cloud engineer. after conversation cloud engineer came up with a aws resource configuration. analyse the conversation and the aws resource configuration and say true if the all resources in the transcript has been accounted in the resource configuration. transcript: {state.transcript}\n\n\n resource configuration: {state.aws_resources}')
        if response.output:
            print('All resources accounted for in the configuration.')
            return 'PASS'
        else:
            print('Retrying to extract resource information.')
            return 'RETRY'
        
    def convertToAzureResources(self, state: State):
        structuredLLM = self.getLLM().with_structured_output(Resources)
        state.azure_resources = structuredLLM.invoke(f'here is a list of aws resources and configuration. convert it to azure specific configuration. \n\nprovided aws configuration : {state.aws_resources}').resources
        return state
    
    def formatedOutput(self, state: State):
        state.output = self.getLLM().invoke(f'Here is the list of azure resources and configuration. \n\n{state.azure_resources} which was generated based on these aws resources: {state.aws_resources}. Convert this in a markdown format for better understanding. Also provide the list of resources in a tabular format with resource name, resource type, and configuration details as columns. Direct information should be provided dont make it sound like a conversational response.').content
        return state

    def buildGraph(self):
        self.getStateGraph().add_node("loadTranscript", self.loadTranscript)
        self.getStateGraph().add_node("extractResourceInformation", self.extractResourceInformation)
        self.getStateGraph().add_node("convertToAzureResources", self.convertToAzureResources)
        self.getStateGraph().add_node("formatedOutput", self.formatedOutput)

        self.getStateGraph().add_edge(self.getStartNodePointer(), "loadTranscript")
        self.getStateGraph().add_edge("loadTranscript", "extractResourceInformation")
        self.getStateGraph().add_conditional_edges(
            "extractResourceInformation",
            self.retryValidator,
            {
                "PASS": 'convertToAzureResources',
                "RETRY": "extractResourceInformation"
            }
        )
        self.getStateGraph().add_edge("convertToAzureResources", "formatedOutput")
        self.getStateGraph().add_edge("formatedOutput", self.getEndNodePointer())