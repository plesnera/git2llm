from dataclasses import dataclass
from typing import List
from src.git_file import GitFile

@dataclass
class GitRepo:
    total_tokens: int
    files: List[GitFile]
    file_count: int

    def __add__(self, other):
        if not isinstance(other, GitRepo):
            raise ValueError("Can only add another GitRepo instance.")

        new_repo = GitRepo(
            total_tokens=self.total_tokens + other.total_tokens,
            files=self.files + other.files,
            file_count=self.file_count + other.file_count
        )

        return new_repo