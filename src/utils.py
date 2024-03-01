#!/usr/bin/env python3

import os
import json
import math
import shutil
import random as rnd
from git import Repo
from pathlib import Path
from typing import List
from src.git_file import GitFile
from src.git_repo import GitRepo


# helper function to create a unique temporary folder
def create_folder(temp_storage_path: Path, repository: str) -> Path:
    folder = temp_storage_path / str(hash(rnd.random())) / Path(repository)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def clone_repo(owner: str, repository: str, token: str, temp_storage_path: Path = Path('temp')) -> Path:
    destination_path = create_folder(temp_storage_path, repository)
    repo_url = f"https://{token}@github.com/{owner}/{repository}.git"
    Repo.clone_from(repo_url, str(destination_path))
    return destination_path


def read_ignore_file(ignore_file_path: Path) -> List[str]:
    ignore_list = []
    if ignore_file_path.is_file():
        with ignore_file_path.open('r') as file:
            for line in file:
                line = line.strip()
                if line == '' or line.startswith('#'):
                    continue
                if line.endswith('/'):
                    line = line + '**'
                line = line.lstrip('/')
                ignore_list.append(line)
    return ignore_list


def windows_to_unix_path(windows_path: str) -> str:
    return windows_path.replace('\\', '/')


def compile_ignore_patterns(repo_path: Path, ignore_file_path: Path, use_gitignore: bool) -> List[str]:
    if not ignore_file_path:
        ignore_file_path = repo_path / '.gptignore'

    ignore_list = read_ignore_file(ignore_file_path)
    ignore_list.extend(['.git/**', '.gitignore'])

    if use_gitignore:
        gitignore_path = repo_path / '.gitignore'
        gitignore_list = read_ignore_file(gitignore_path)
        ignore_list.extend(gitignore_list)

    final_ignore_list = [
        os.path.join(repo_path, pattern) if os.path.isdir(os.path.join(repo_path, pattern)) else pattern for pattern in
        ignore_list]
    return final_ignore_list


def estimate_tokens(output: str) -> int:
    token_count = len(output) / 3.5  # Based on a rough ratio for GPT-4 of 3.5 tokens per character
    return math.ceil(token_count)


def process_file(file_path: Path, repo_root: Path, repo: GitRepo) -> None:
    with file_path.open('r', encoding='utf-8', errors='ignore') as file:
        contents = file.read()
        relative_path = file_path.relative_to(repo_root).as_posix()
        file = GitFile(path=relative_path, tokens=estimate_tokens(contents), contents=contents)
        repo.files.append(file)


def process_repo(repo_path: Path, files_to_ignore: List[Path]) -> GitRepo:
    repo_object = GitRepo(total_tokens=0, files=[], file_count=0)
    for element in repo_path.rglob('*'):
        if element.as_posix() not in files_to_ignore and element.is_file():
            process_file(element, repo_path, repo_object)
    repo_object.file_count = len(repo_object.files)
    return repo_object


def output_git_repo(repo: GitRepo) -> str:
    repo_builder = list()
    repo_builder.append("The following text is a Git repository with code."
                        "The structure of the text are sections that begin with ----, "
                        "followed by a single line containing the file path and file name, "
                        "followed by a variable amount of lines containing the file contents. "
                        "The text representing the Git repository ends when the symbols --END-- are encountered. "
                        "Any further text beyond --END-- are meant to be interpreted as instructions "
                        "using the aforementioned Git repository as context.\n")

    for file in repo.files:
        repo_builder.append("----\n")
        repo_builder.append(f"{file.path}\n")
        repo_builder.append(f"{file.contents}\n")

    repo_builder.append("--END--")
    output = ''.join(repo_builder)
    repo.total_tokens = estimate_tokens(output)
    return output


def marshal_repo(git_repo: Repo) -> str:
    try:
        return json.dumps(git_repo, default=lambda x: x.__dict__, indent=4)
    except Exception as e:
        raise ValueError(f"Error marshalling repo: {e}")


def produce_output(git_repo, output_json: bool = False, write_to_path: str = "") -> int:
    # converts the repo object into a text or json object
    if output_json:
        repo_as_text = marshal_repo(git_repo)
    else:
        repo_as_text = output_git_repo(git_repo)

    if write_to_path:
        # if output file exists, throw error
        with open(write_to_path, "a") as f:
            f.write(repo_as_text)
    else:
        print(repo_as_text)
    return estimate_tokens(repo_as_text)


def list_files_to_ignore_in_repo(ignore_list: List[str], repo_source_path: Path):
    file_list = []
    for ignore_item in ignore_list:
        matches = repo_source_path.glob(ignore_item)
        for match in matches:
            if match:
                file_list.append(match)
    return file_list


def remove_temp_repo(repo_path: Path) -> None:
    shutil.rmtree(repo_path.parent)
    return
