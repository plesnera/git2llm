# Git 2 LLM 
### Convert a Github repo to a doc with markup for use with a LLM

This project is a python adaptation of a project written in Golang by chand1012.
https://github.com/chand1012/git2gpt.git

This Python script is designed to clone a GitHub repository, process its files, and generate an output. The output can be either a text representation of the repository or a JSON object. The script also provides an option to estimate the number of tokens in the output.

### Features
* Clones a GitHub repository to a local temporary folder.
* Process all files in the repository, excluding those specified in .gitignore and an additional ignore file (.gptignore by default).
* Generate a text representation or a JSON object of the repository.
* Estimate the number of tokens in the output.

### Usage
The script is intended to be run from the command line with the following environment variables:
* REPO_OWNER: The owner of the GitHub repository.
* REPO_NAME: The name of the GitHub repository.
* GITHUB_ACCESS_TOKEN: A personal access token for GitHub to ensure that private repos can be accessed.
You can also pass these parameters directly to the main() function in the script.


Additional optional parameters for the main() function include:
* local_storage: The path on the file system where the repository should be cloned. Defaults to 'temp'.
* additional_ignore_file: Path to an optional file specifying patterns to ignore. Defaults to '.gptignore' (missing file will be ignored).
* use_gitignore: Defaults to True, so that gitignore is used to determine what to skip from extraction.
* output_json: If True, the output will be in JSON format. Defaults to False.
* write_filepath: The filepath and name to write output to. If empty, output is printed to screen.
* yield_tokens_estimate: If True, the total number of tokens will be printed to std out. Defaults to False.
  
  ### Dependencies
  The script requires the following Python packages:
  * os
  * json
  * math
  * shutil
  * random
  * git
  * dataclasses
  * typing
  * pathlib

  Please ensure these are installed before running the script.
