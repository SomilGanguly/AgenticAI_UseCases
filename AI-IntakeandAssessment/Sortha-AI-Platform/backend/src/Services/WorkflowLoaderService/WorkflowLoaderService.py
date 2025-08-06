import os
import sys
from src.Services.WorkflowLoaderService.WorkflowLoader import WorkflowLoader

class WorkflowLoaderService:
    __instance = None
    def __init__(self):
        if WorkflowLoaderService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            WorkflowLoaderService.__instance = self
            self.__baseLocation = None
            self.__workflow = {}

    def add_path_to_sys(path: str):
        if path not in sys.path:
            sys.path.append(path)

    @staticmethod
    def get_instance():
        if WorkflowLoaderService.__instance is None:
            WorkflowLoaderService()
        return WorkflowLoaderService.__instance
    
    def set_base_location(self, base_location):
        if not os.path.exists(base_location):
            raise Exception(f"Base location '{base_location}' does not exist.")
        WorkflowLoaderService.add_path_to_sys(base_location)
        self.__baseLocation = base_location

    # Check for all the workflows in the base location
    def refresh(self):
        if self.__baseLocation is None:
            raise Exception("Base location is not set.")

        for dir in os.listdir(self.__baseLocation):
            self.__workflow[dir] = None
        
        print(f"Workflows found: {list(self.__workflow.keys())}")

    # Reload all workflows from the base location
    def reload_all_workflows(self):
        for i in self.__workflow:
            try:
                self.__workflow[i] = WorkflowLoader(self.__baseLocation, i).build()
            except Exception as e:
                print(f"Error loading workflow '{i}': {e}")

    def get_all_workflows(self):
        if not self.__workflow:
            return []
        return [self.__workflow[i] for i in self.__workflow if self.__workflow[i] is not None]