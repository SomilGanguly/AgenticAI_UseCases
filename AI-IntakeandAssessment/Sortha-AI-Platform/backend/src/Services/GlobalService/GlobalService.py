from ...Utils.Sortha import SorthaDBService
from ...Services.LogPipe.LogPipe import LogPipe
from ...Services.FileService.FileService import FileService

class GlobalService:
    _instance = None
    def __init__(self, *args):
        if GlobalService._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GlobalService._instance = self
            self.sorthDbService = None

    @staticmethod
    def get_instance():
        if GlobalService._instance is None:
            raise Exception("GlobalService instance not initialized. Call initialize() first.")
        return GlobalService._instance
    
    def register(self, service):
        if isinstance(service, SorthaDBService):
            self.sorthDbService = service
        elif isinstance(service, LogPipe):
            self.logService = service
        elif isinstance(service, FileService):
            self.fileService = service
        else:
            raise TypeError("Service Registration not Supported.")

    def get_sorthDBService(self):
        if self.sorthDbService is None:
            raise Exception("SorthaDBService not registered. Call register() first.")
        return self.sorthDbService
    
    def get_logService(self):
        if not hasattr(self, 'logService'):
            raise Exception("LogPipe not registered. Call register() first.")
        return self.logService
    
    def get_fileService(self):
        if not hasattr(self, 'fileService'):
            raise Exception("FileService not registered. Call register() first.")
        return self.fileService