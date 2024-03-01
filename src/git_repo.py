from dataclasses import dataclass

@dataclass
class GitRepo:
    total_tokens: int
    files: List[GitFile]
    file_count: int