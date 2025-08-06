from abc import ABC, abstractmethod
from typing import BinaryIO, Generator

class FileService(ABC):
    @abstractmethod
    def create_file(self, file: BinaryIO, file_ext: str) -> str:
        """Creates a file to the specified destination."""
        pass

    @abstractmethod
    def read_file(self, file_name: str) -> Generator[bytes, None, None]:
        """Creates a file Generator from the specified ID to the destination."""
        pass

    @abstractmethod
    def file_exists(self, file_name: str) -> bool:
        """Checks if a file exists in the specified destination."""
        pass

    @abstractmethod
    def delete_file(self, file_name: str) -> None:
        """Deletes a file from the specified destination."""
        pass