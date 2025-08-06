from SorthaAI.SorthaAIService import SorthaAIService
from SorthaAI.Models.ExecutionState import Status as ExecutionStatus
import time
import importlib
import sys
from Utils.Agent import createOpenAIClient
from Utils.Serializer import addable_values_dict_to_json
import msvcrt
from fire import Fire
from pathlib import Path
import os
import Utils.ConstantFileContent as ConstantFileContent
from SorthaAI.WorkFlow import StateBase, WorkFlowBase

def wait_for_any_key():
    print("Press any key to continue...")
    msvcrt.getch() # Waits for a single character input without echoing it

def add_path_to_sys(path: str):
    if path not in sys.path:
        sys.path.append(path)

def load_module(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
        return None

class SorthaDevKit:
    def init(self, path: str=None):
        if path is None:
            path = str(Path().resolve())

        os.makedirs(path, exist_ok=True)

        with open(f'{path}\\.env', 'w') as f:
            f.write(ConstantFileContent.getEnvContent())
        
        with open(f'{path}\\Config.py', 'w') as f:
            f.write(ConstantFileContent.getConfigContent(path))
        
        with open(f'{path}\\Input.py', 'w') as f:
            f.write(ConstantFileContent.getInputContent())
        
        with open(f'{path}\\State.py', 'w') as f:
            f.write(ConstantFileContent.getStateContent())
        
        with open(f'{path}\\WorkFlow.py', 'w') as f:
            f.write(ConstantFileContent.getWorkFlowContent())

    def run(self, module_path: str=None):
        if module_path is None:
            module_path = str(Path().resolve())

        add_path_to_sys(module_path)

        sys.modules['StateBase'] = StateBase
        sys.modules['WorkFlowBase'] = WorkFlowBase
        
        stateMod = importlib.import_module('State')
        configMod = importlib.import_module('Config')
        workflowMod = importlib.import_module('WorkFlow')
        inputMod = importlib.import_module('Input')
        
        llmCred = configMod.LLMConfig()
        llm = createOpenAIClient(AZURE_OPENAI_DEPLOYMENT_NAME=llmCred.AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_MODEL_NAME=llmCred.AZURE_OPENAI_MODEL_NAME, AZURE_OPENAI_TEMPERATURE=llmCred.AZURE_OPENAI_TEMPERATURE, AZURE_OPENAI_API_KEY=llmCred.AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT=llmCred.AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION=llmCred.AZURE_OPENAI_API_VERSION)
        SorthaAIService(llm)

        stateInputs = inputMod.Input
        
        wf = workflowMod.CustomWorkFlow(llm)
        wf.createStateGraph(stateMod.State)
        wf.buildGraph()
        inputState = stateMod.State(
            inputs=stateInputs
        )
        
        wfId = SorthaAIService.get_instance().invoke_workflow(wf, inputState)

        counter = 0
        while SorthaAIService.get_instance().get_execution_status(wfId) not in [ExecutionStatus.completed, ExecutionStatus.failed]:
            print(f"Workflow {wfId} is still running... ({counter}s)", end='\r')
            time.sleep(1)
            counter += 1
        print()

        result = SorthaAIService.get_instance().get_execution_result(wfId)
        
        if type(result) is str:
            print(f"Workflow {wfId} completed with result: \n{result}")
        else:
            result.pop('inputs', None)
            print(f"Workflow {wfId} completed with result: \n{addable_values_dict_to_json(result)}")
        
        wait_for_any_key()


if __name__ == '__main__':
    Fire(SorthaDevKit)
