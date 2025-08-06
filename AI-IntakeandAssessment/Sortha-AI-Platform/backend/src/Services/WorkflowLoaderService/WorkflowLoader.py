import importlib
import sys

class WorkflowLoader:
    def __init__(self, workflow_path, workflow_name):
        self.workflow_path = workflow_path
        self.workflow_name = workflow_name
        self.inputConfig = None
        self.metadataConfig = None
        self.stateClass = None
        self.workflowClass = None
        self.load_components()

    def load_components(self):
        try:
            self.loadConfig()
            self.loadState()
            self.loadWorkflow()
        except Exception as e:
            raise Exception(f"Error loading components from {self.workflow_name}: {e}")

    def loadConfig(self):
        configClass = importlib.import_module(self.workflow_name + '.Config')
        if not hasattr(configClass, 'InputConfig'):
            raise Exception(f"InputConfig class not found in {self.workflow_name}.Config")
        if not hasattr(configClass.InputConfig, 'inputs'):
            raise Exception(f"InputConfig.inputs not found in {self.workflow_name}.Config")
        if not hasattr(configClass.InputConfig, 'metadata'):
            raise Exception(f"InputConfig.metadata not found in {self.workflow_name}.Config")
        self.inputConfig = configClass.InputConfig.inputs
        self.metadataConfig = configClass.InputConfig.metadata

    def loadState(self):
        stateClass = importlib.import_module(self.workflow_name + '.State')
        if not hasattr(stateClass, 'State'):
            raise Exception(f"State class not found in {self.workflow_name}.State")
        self.stateClass = stateClass.State

    def loadWorkflow(self):
        workflowClass = importlib.import_module(self.workflow_name + '.WorkFlow')
        if not hasattr(workflowClass, 'CustomWorkFlow'):
            raise Exception(f"CustomWorkFlow class not found in {self.workflow_name}.WorkFlow")
        self.workflowClass = workflowClass.CustomWorkFlow

    def build(self):
        return [self.metadataConfig['name'], self.metadataConfig['description'], self.stateClass, self.workflowClass, self.inputConfig]