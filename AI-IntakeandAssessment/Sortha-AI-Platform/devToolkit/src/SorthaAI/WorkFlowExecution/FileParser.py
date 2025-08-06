from ..WorkFlow.StateBase import StateBase, FileInputType, FileTypes
from os import path
import importlib
import pandas as pd

class FileParser:
    def __init__(self, state: StateBase):
        self.state = state

    def execute(self) -> StateBase:
        for key, value in self.state.inputs.items():
            if isinstance(value.type, FileTypes) and value.type == FileTypes.TEXT:
                self.state.inputs[key].content = FileParser.text_parser(value.file_path)
            elif isinstance(value.type, FileTypes) and value.type == FileTypes.EXCEL:
                self.state.inputs[key].content = FileParser.excel_parser(value.file_path)
            else:
                raise ValueError(f"Unsupported file type for key '{key}': {value.type}")
            
        return self.state
            
    def text_parser(file_path: str) -> str:
        if not path.exists(file_path):
            raise ValueError(f"File '{file_path}' not found.")
        
        file_content = ''
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        return file_content.strip()
    
    def excel_parser(file_path: str):
        sheets=pd.read_excel(file_path, engine='openpyxl', sheet_name=None)
        return sheets.items()