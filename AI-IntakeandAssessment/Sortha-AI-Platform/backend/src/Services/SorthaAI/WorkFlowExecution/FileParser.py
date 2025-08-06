from ..WorkFlow.StateBase import StateBase, FileInputType, FileTypes
from ...GlobalService.GlobalService import GlobalService
from src.Schemas.File import File
from database import get_db

class FileParser:
    def __init__(self, state: StateBase):
        self.state = state

    def execute(self) -> StateBase:
        for key, value in self.state.inputs.items():
            if value.type == FileTypes.TEXT.value:
                self.state.inputs[key].content = FileParser.text_parser(value.file_id)
            elif value.type == FileTypes.EXCEL.value:
                # Handle Excel files if needed
                pass
            else:
                # Handle other types or raise an error
                raise ValueError(f"Unsupported file type for key '{key}': {value.type}")
            
        return self.state
            
    def text_parser(file_id: int) -> str:
        fs = GlobalService.get_instance().get_fileService()
        db = next(get_db())
        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            raise ValueError(f"File with id '{file_id}' not found.")
        
        file_content = next(fs.read_file(file.file_physcial_address)).decode('utf-8')

        return file_content.strip()