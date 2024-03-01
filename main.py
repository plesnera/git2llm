#!/usr/bin/env python3
import os

from src.utils import (_clone_repo, _compile_ignore_patterns, _list_files_to_ignore_in_repo,
                       _process_repo, _produce_output, _remove_temp_repo)


def main(
    owner: str,
    git_repo: str,
    token: str,
    local_storage: str = "temp",
    additional_ignore_file: str = "",
    ignore_gitignore: bool = False,
    output_json: bool = False,
    write_filepath: str = "",
    yield_tokens_estimate: bool = False
) -> None:
    """
     Clones a GitHub repository, processes its files, and generates an output.

     Args:
         owner (str): The owner of the GitHub repository.
         git_repo (str): The name of the GitHub repository.
         token (str): A personal access token for GitHub.
         local_storage (str, optional): The path where the repository should be cloned. Defaults to 'temp'.
         additional_ignore_file (str, optional): Path to an additional file specifying patterns to ignore. Defaults to ''.
         ignore_gitignore (bool, optional): If True, .gitignore files will be ignored. Defaults to False.
         output_json (bool, optional): If True, the output will be in JSON format. Defaults to False.
         write_filepath (str, optional): The filepath and name to write output to. If empty, output is printed to screen. Defaults to "".
         yield_tokens_estimate (bool, optional): If True, the function will also estimate the number of tokens in the output. Defaults to False.

     Returns:
         None: The function doesn't return anything. It either prints the output or writes it to a file.
     """

    # clones repository to local temp folder
    repo_path=_clone_repo(owner=owner, repository=git_repo, token=token, temp_storage_path=local_storage)
    # outputs a combined list of files to ignore looking for the .gitignore as well as an additional .gptignore file
    combine_ignore_lists = _compile_ignore_patterns(repo_path, additional_ignore_file, not ignore_gitignore)
    # returns a list object of any file in the repo matching the ignore criteria
    files_to_ignore = _list_files_to_ignore_in_repo(combine_ignore_lists, repo_path)
    # produces an object containing all repo elements
    git_repo = _process_repo(repo_path, files_to_ignore)

    # print output to screen or produce an output file with text or json and return a token count
    token_count = _produce_output(git_repo, output_json, write_filepath)
    # clean up and remove temp repo again
    _remove_temp_repo(repo_path)
    # prints a approximated token estimation
    if yield_tokens_estimate:
        print(token_count)

    return None



if __name__ == "__main__":
    main(owner=os.environ["REPO_OWNER"],git_repo=os.environ["REPO_NAME"],token=os.environ["GITHUB_ACCESS_TOKEN"])
