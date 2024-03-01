from dataclasses import dataclass


@dataclass
class GitFile:
    path: str
    tokens: int
    contents: str