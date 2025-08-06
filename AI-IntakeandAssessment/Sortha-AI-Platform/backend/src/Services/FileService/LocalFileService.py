from os import mkdir, remove, path
from .FileService import FileService
from typing import BinaryIO, Generator
from uuid import uuid4
import shutil

class LocalFileService(FileService):
    _instance = None

    def __init__(self, base_path: str):
        if LocalFileService._instance is not None:
            raise Exception("This class is a singleton!")
        LocalFileService._instance = self
        self.base_path = base_path
        LocalFileService.__create_base_directory(base_path)

    @staticmethod
    def get_instance():
        """Returns the singleton instance of FileService."""
        if LocalFileService._instance is None:
            raise Exception("FileService instance not created yet.")
        return LocalFileService._instance

    def __create_base_directory(base_path: str) -> None:
        if not path.exists(base_path):
            print(f"Creating base directory at {base_path}")
            mkdir(base_path)
        else:
            print(f"Base directory already exists at {base_path}")

    def clear_all_files(self) -> None:
        """Clears all files in the base directory."""
        if path.exists(self.base_path):
            print(f"Clearing all files in {self.base_path}")
            shutil.rmtree(self.base_path)
        LocalFileService.__create_base_directory(self.base_path)

    def create_file(self, file: BinaryIO, file_ext: str) -> str:
        file_name = f"{uuid4()}.{file_ext}"
        with open(f'{self.base_path}/{file_name}', 'wb') as f:
            f.write(file.read())

        return file_name

    def read_file(self, file_name: str) -> Generator[bytes, None, None]:
        if not self.file_exists(file_name):
            raise FileNotFoundError(f"File {file_name} does not exist in {self.base_path}")
        with open(f'{self.base_path}/{file_name}', 'rb') as f:
            yield f.read()

    def file_exists(self, file_name: str) -> bool:
        full_path = f'{self.base_path}/{file_name}'
        return path.exists(full_path)

    def delete_file(self, file_name: str) -> None:
        full_path = f'{self.base_path}/{file_name}'
        if not self.file_exists(file_name):
            raise FileNotFoundError(f"File {file_name} does not exist in {self.base_path}")
        remove(full_path)