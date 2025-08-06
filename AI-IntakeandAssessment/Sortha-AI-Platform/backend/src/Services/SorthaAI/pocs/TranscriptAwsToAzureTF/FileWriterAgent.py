from pathlib import Path
from .State import TerraformCode

class FileWriterAgent:
    def __init__(self, home_directory: str):
        self.home_directory = home_directory

    def writeFile(self, file: list[TerraformCode]):
        for tf_code in file:
            path = tf_code.path.replace('/', '\\') # Ensure Windows-style path
            file_path = f"{self.home_directory}\\{path}"
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w+', encoding='utf-8') as f:
                f.write(tf_code.content)
            print(f"File written to {file_path}")