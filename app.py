#/usr/bin/env python3

import os
import json
import math
import glob
from git import Repo
from dataclasses import dataclass
from typing import List, Optional, Generator

@dataclass
class GitFile:
    path: str
    tokens: int
    contents: str

@dataclass
class GitRepo:
    total_tokens: int
    files: List[GitFile]
    file_count: int

def _destination_path_ready(destination_path:str) -> bool:
    return os.path.isdir(destination_path) and not bool([True for _ in os.scandir(destination_path)])

def _clone_repo(owner:str, repository:str, destination_path: str, token:str) -> None:
    """
    Takes an owner, repo and auth token for a GitHub repository ad.

    Args:
        github_url (str): The URL of the GitHub repository to clone.
        destination_path (str): The path on the file system where the repository should be cloned.
    """
    if _destination_path_ready(destination_path):
        repo_url=f"https://{token}@github.com/{owner}/{repository}.git"
        Repo.clone_from(repo_url, destination_path)
    else:
        print('Destination Path does not exist or is not empty')


def _read_ignore_file(ignore_file_path: str) -> List[str]:
    ignore_list = []
    try:
        with open(ignore_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line == '' or line.startswith('#'):
                    continue
                if line.endswith('/'):
                    line = line + '**'
                line = line.lstrip('/')
                ignore_list.append(line)
    except FileNotFoundError:
        pass
    return ignore_list

def _windows_to_unix_path(windows_path: str) -> str:
    return windows_path.replace('\\', '/')

def _compile_ignore_patterns(repo_path: str, ignore_file_path: str = '', use_gitignore: bool = True) -> List[str]:
    if not ignore_file_path:
        ignore_file_path = os.path.join(repo_path, '.gptignore')

    ignore_list = _read_ignore_file(ignore_file_path)
    ignore_list.extend(['.git/**', '.gitignore'])

    if use_gitignore:
        gitignore_path = os.path.join(repo_path, '.gitignore')
        gitignore_list = _read_ignore_file(gitignore_path)
        ignore_list.extend(gitignore_list)

    final_ignore_list = [os.path.join(repo_path, pattern) if os.path.isdir(os.path.join(repo_path, pattern)) else pattern for pattern in ignore_list]
    return final_ignore_list

def estimate_tokens(output:str) -> int:
    token_count = len(output) / 3.5  # Based on a rough ratio for GPT-4 of 3.5 tokens per character
    return math.ceil(token_count)

def _process_file(file_path: str, repo: GitRepo) -> None:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        contents = file.read()
        # if is_valid_utf8(contents):
        file = GitFile(path=file_path, tokens=estimate_tokens(contents), contents=contents)
        repo.files.append(file)

def iterate_and_process_repo(repo_path: str, files_to_ignore: List[str]) -> GitRepo:
    repo = GitRepo(total_tokens=0, files=[], file_count=0)
    for root, _, files in os.walk(repo_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path not in files_to_ignore:
                _process_file(file_path, repo)
    repo.file_count = len(repo.files)
    return repo

def output_git_repo(repo: GitRepo) -> str:
    repo_builder = []
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

def _marshal_repo(repo: GitRepo) -> str:
    try:
        output_git_repo(repo, '')
        return json.dumps(repo.__dict__)
    except Exception as e:
        raise ValueError(f"Error marshalling repo: {e}")


def _list_files_to_ignore_in_repo(ignore_list: List[str], repo_source_path:str):
    unix_path=_windows_to_unix_path(repo_source_path)
    file_list=[]
    for ignore_item in ignore_list:
        matches=glob.glob(unix_path+'/'+ignore_item, recursive=True)
        for match in matches:
            if match:
                file_list.append(match)
    return file_list


def main(
    repo_source_path: str,
    additional_ignore_file: str="",
    ignore_gitignore: bool=False,
    output_json: str="",
    output_file: str="",
    yield_tokens_estimate: bool=False
) -> None:
    """
Main function to process a Git repository and generate output.

Args:
    repo_source_path (str): The fully qualified path to the Git repository to process.
    additional_ignore_file (str): Path to an additional file specifying patterns to ignore.
    ignore_gitignore (bool, optional): If True, .gitignore files will be ignored. Defaults to False.
    output_json (str, optional): If provided, the output will be in JSON format. Defaults to "".
    output_file (str): The path to the file where the output will be written.
    yield_tokens_estimate (bool, optional): If True, the function will also estimate the number of tokens in the output. Defaults to False.

Returns:
    None
"""
    combine_ignore_list = _compile_ignore_patterns(repo_source_path, additional_ignore_file, not ignore_gitignore)
    files_to_ignore = _list_files_to_ignore_in_repo(combine_ignore_list, repo_source_path)
    repo = iterate_and_process_repo(repo_source_path, files_to_ignore)
    output_text=output_git_repo(repo)

    if yield_tokens_estimate:
        print(estimate_tokens(output_text))

    if output_json:
        output, err = _marshal_repo(repo)
        if err:
            print(err)
            exit(1)

    if output_file:
        # if output file exists, throw error
        if os.path.exists(output_file):
            print(f"Error: output file {output_file} already exists")
            exit(1)
        with open(output_file, "w") as f:
            f.write(output_text)
    else:
        print(output_text)
    return


if __name__ == "__main__":
    _clone_repo('plesnera', 'faker', 'cloned_repo','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')
    # args = main(repo_source_path='cloned_repo/')
    # print(_destination_path_ready('/Users/plesnera/IdeaProjects/AI-powered/git2text/empty'))


