from ...WorkFlow.WorkFlowBase import WorkFlowBase
from .State import State, Resources, YesOrNo

class TranscriptToAIF(WorkFlowBase):
    def loadTranscript(self, state: State):
        content = ''
        with open(state.transcript.source_path, 'r') as file:
            content = file.read()
        state.transcript.content = content
        return state
    
    def extractResourceInformation(self, state: State):
        structuredLLM = self.getLLM().with_structured_output(Resources)
        state.aws_resources = structuredLLM.invoke(f'Provided following is the transcript generated after conversing with the customer. Analyse the conversation and predict the aws resouce configuration for the application: {state.transcript.content}').resources
        state.retry_count += 1
        return state
    
    def retryValidator(self, state: State):
        if state.retry_count >= state.retry_limit:
            print('Retry limit reached. Exiting workflow.')
            return 'PASS'
        
        structuredLLM = self.getLLM().with_structured_output(YesOrNo)
        response = structuredLLM.invoke(f'A conversation happend between the customer and cloud engineer. after conversation cloud engineer came up with a aws resource configuration. analyse the conversation and the aws resource configuration and say true if the all resources in the transcript has been accounted in the resource configuration. transcript: {state.transcript.content}\n\n\n resource configuration: {state.aws_resources}')
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
    
    def buildGraph(self):
        self.getStateGraph().add_node("loadTranscript", self.loadTranscript)
        self.getStateGraph().add_node("extractResourceInformation", self.extractResourceInformation)
        self.getStateGraph().add_node("convertToAzureResources", self.convertToAzureResources)

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
        self.getStateGraph().add_edge("convertToAzureResources", self.getEndNodePointer())