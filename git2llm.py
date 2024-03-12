#!/usr/bin/env python3
import os
from pathlib import Path
import argparse
from src.utils import (clone_repo, compile_ignore_patterns, list_files_to_ignore_in_repo,
                       process_repo, produce_output, remove_temp_repo)

def run(owner: str,
        repo_name: str,
        token: str,
        additional_ignore_file: Path,
        temp_local_storage: Path=Path('temp'),
        use_gitignore: bool=True,
        output_json: bool = False,
        output_filepath: str = "",
        yield_token_estimate: bool = False
        ) -> None:

    # clones repository to local temp folder
    repo_path = clone_repo(owner=owner, repository=repo_name, token=token, temp_storage_path=temp_local_storage)
    # outputs a combined list of files to ignore looking for the .gitignore as well as an additional .gptignore file
    combine_ignore_lists = compile_ignore_patterns(repo_path=repo_path, ignore_file_path=additional_ignore_file, use_gitignore=use_gitignore)
    # returns a list object of any file in the repo matching the ignore criteria
    files_to_ignore = list_files_to_ignore_in_repo(combine_ignore_lists, repo_path)
    # produces an object containing all repo elements
    git_repo_processed = process_repo(repo_path, files_to_ignore)
    # print output to screen or produce an output file with text or json and return a token count
    token_count = produce_output(git_repo_processed, output_json, output_filepath)
    # clean up and remove temp repo again
    remove_temp_repo(repo_path)
    # prints a approximated token estimation
    if yield_token_estimate:
        print(token_count)

    return None

def main():
    """
     Clones a GitHub repository, processes its files, and generates an output.

     Args:
         owner (str): The owner of the GitHub repository.
         repo_name (str): The name of the GitHub repository.
         token (str): A personal access token for GitHub.
         local_storage (str, optional): The path where the repository should be cloned. Defaults to 'temp' in the repo where this code is running.
         additional_ignore_file (str, optional): Path to an optional file specifying patterns to ignore. Defaults to '.gptignore'.
         use_gitignore (bool, optional): If False, .gitignore files will be ignored. Defaults to True.
         output_json (bool, optional): If True, the output will be in JSON format. Defaults to False.
         write_filepath (str, optional): The filepath and name to write output to. If empty, output is printed to screen. Defaults to "".
         yield_tokens_estimate (bool, optional): If True, the function will also estimate the number of tokens in the output. Defaults to False.

     Returns:
         None: The function doesn't return anything. It either prints the output or writes it to a file.
     """
    parser = argparse.ArgumentParser(description="Process a GitHub repository and generate output.")
    parser.add_argument('owner', help='The owner of the GitHub repository.')
    parser.add_argument('repo_name', help='The name of the GitHub repository.')
    parser.add_argument('token', help='A personal access token for GitHub.')
    parser.add_argument('--additional_ignore_file', help='Path to an additional file specifying file patterns to ignore.')
    parser.add_argument('--temp_local_storage', default=Path('temp'), help='The path where the repository should be cloned to.')
    parser.add_argument('--use_gitignore', default=True, action='store_true', help='If set to False, .gitignore files will be ignored.')
    parser.add_argument('--output_json', action='store_true', help='If set, the output will be in JSON format.')
    parser.add_argument('--output_filepath', default='', help='The filepath and name to write output to.')
    parser.add_argument('--yield_token_estimate', action='store_true', help='If set, the function will also estimate the number of tokens in the output.')

    args = parser.parse_args()
    print(f"Will clone the Github repository '{args.repo_name}' for owner '{args.owner}'"
          f"into '{args.temp_local_storage}' and save the processed output to "
          f"{args.write_filepath if args.write_filepath else 'Screen'}")
    # Call your existing function with the arguments
    run(
        owner=args.owner,
        repo_name=args.repo_name,
        token=args.token,
        additional_ignore_file=Path(args.additional_ignore_file),
        temp_local_storage=args.temp_local_storage,
        use_gitignore=args.use_gitignore,
        output_json=args.output_json,
        output_filepath=args.write_filepath,
        yield_token_estimate=args.yield_token_estimate
    )

if __name__ == "__main__":
    main()

