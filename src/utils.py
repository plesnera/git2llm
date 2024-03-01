import os
import json
import math
import glob
import random as rnd
from git import Repo
from typing import List
from src.git_file import GitFile
from src.git_repo import GitRepo


# helper function to create a unique temporary folder
def _create_folder(temp_storage_path, repository: str):
    folder = f"{temp_storage_path}/{str(hash(rnd.random()))}/{repository}"
    os.mkdir(folder)
    return folder


def _clone_repo(owner: str, repository: str, token: str, temp_storage_path: str = 'temp') -> str:
    """
    Takes an owner, repo and auth token for a GitHub repository ad.

    Args:
        owner (str): The owner of the GitHub repo.
        repository (str): The GitHu Repository.
        token (str): A personal access token for GitHu to ensure that private repos can be accessed.
        temp_storage_path (str): The path on the file system where the repository should be cloned.
    """
    destination_path = _create_folder(temp_storage_path, repository)
    repo_url = f"https://{token}@github.com/{owner}/{repository}.git"
    Repo.clone_from(repo_url, destination_path)
    return destination_path


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

    final_ignore_list = [
        os.path.join(repo_path, pattern) if os.path.isdir(os.path.join(repo_path, pattern)) else pattern for pattern in
        ignore_list]
    return final_ignore_list


def _estimate_tokens(output: str) -> int:
    token_count = len(output) / 3.5  # Based on a rough ratio for GPT-4 of 3.5 tokens per character
    return math.ceil(token_count)


def _process_file(file_path: str, repo: GitRepo) -> None:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        contents = file.read()
        # if is_valid_utf8(contents):
        file = GitFile(path=file_path, tokens=_estimate_tokens(contents), contents=contents)
        repo.files.append(file)


def _process_repo(repo_path: str, files_to_ignore: List[str]) -> GitRepo:
    repo = GitRepo(total_tokens=0, files=[], file_count=0)
    for root, _, files in os.walk(repo_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path not in files_to_ignore:
                _process_file(file_path, repo)
    repo.file_count = len(repo.files)
    return repo


def _output_git_repo(repo: GitRepo) -> str:
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
    repo.total_tokens = _estimate_tokens(output)
    return output


def _marshal_repo(git_repo: Repo) -> str:
    try:
        return json.dumps(git_repo, default=lambda x: x.__dict__, indent=4)
    except Exception as e:
        raise ValueError(f"Error marshalling repo: {e}")


def _produce_output(git_repo, output_json: bool = False, write_to_path: str = "") -> int:
    # converts the repo object into a text or json object

    if output_json:
        repo_as_text = _marshal_repo(git_repo)
    else:
        repo_as_text = _output_git_repo(git_repo)

    if write_to_path:
        # if output file exists, throw error
        with open(write_to_path, "a") as f:
            f.write(repo_as_text)
    else:
        print(repo_as_text)
    return _estimate_tokens(repo_as_text)


def _list_files_to_ignore_in_repo(ignore_list: List[str], repo_source_path: str):
    unix_path = _windows_to_unix_path(repo_source_path)
    file_list = []
    for ignore_item in ignore_list:
        matches = glob.glob(unix_path + '/' + ignore_item, recursive=True)
        for match in matches:
            if match:
                file_list.append(match)
    return file_list


def _remove_temp_repo(repo_path: str) -> None:
    os.system(f"rm -rf {repo_path}")
    return
