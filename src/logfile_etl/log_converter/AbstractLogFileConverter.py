from abc import ABC, abstractmethod
from pathlib import Path


class AbstractLogFileConverter(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def does_applies_for_file(self, filename) -> bool:
        pass

    @abstractmethod
    def convert_log_file(
        self, filename, file_path: Path, writing_directory: Path
    ) -> bool:
        pass
