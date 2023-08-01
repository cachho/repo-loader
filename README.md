# repo-loader

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)
[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

This is a fork of the very excellent [gptrepo](https://github.com/zackees/gptrepo) by zackees, which itself is a fork of [gpt-repository-loader](https://github.com/mpoon/gpt-repository-loader) by mpoon.

This tool concatenates through all the files in the repo and adds ai prompts which can be used for chat gpt conversations.

Simply open up the file, copy and paste it into the chat gpt window and then ask your question about the code.

## Features

- dump entire code of github repository into a single file
- easy to split if you want to embed single files
- respect .gitignore and .gptignore
- show progress bar
- use in CLI and scripts

## Usage

### CLI

```python
pip install repo-loader
repo-loader  # now output.txt should appear in the current directory
```

### Script

```python
from repo_loader import repo_loader
repo_loader.load("example_repo")
```

### Options

| Argument                     | Type | Default                                                                                                                         | Description                                                             |
| ---------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `repo_path`                  | str  | Current directory                                                                                                               | The path to the git repository to be processed.                         |
| `out_path`                   | str  | 'output.txt'                                                                                                                    | The path to the output file.                                            |
| `preamble_file`              | str  | None                                                                                                                            | The path to a preamble file. Contents are written to output first.      |
| `preamble`                   | str  | [here](https://github.com/cachho/repo-loader/blob/9801bbe6e879455376a337cf207db2dcc30d8225/src/repo_loader/repo_loader.py#L184) | Text that will be written to the output file before the repo contents.  |
| `clipboard`                  | bool | False                                                                                                                           | If True, output is copied to the clipboard instead of a file.           |
| `quiet`                      | bool | False                                                                                                                           | If True, the script will not print to stdout or auto-open the file.     |
| `progress`                   | bool | False                                                                                                                           | If True, the script will display a progress bar during processing.      |
| `open_file_after_processing` | bool | False                                                                                                                           | If True, the output file will be automatically opened after processing. |

## Description

`repo-loader` is a command-line and script tool that converts the contents of a Git repository into a text format, preserving the structure of the files and file contents. The generated output can be interpreted by AI language models, allowing them to process the repository's contents for various tasks, such as code review or documentation generation.

## Contributing

Some context around building this is [located here](https://github.com/mpoon/gpt-repository-loader/discussions/18). Appreciate any issues and pull requests in the spirit of having mostly GPT build out this tool. Using [ChatGPT Plus](https://chat.openai.com/) is recommended for quick access to GPT-4.

## Running Tests

To run the tests for `repo-loader`, follow these steps:

1. Ensure you have Python 3 installed on your system.
2. Navigate to the repository's root directory in your terminal.
3. Run the tests with the following command:

   ```bash
   tox
   ```

   Now, the test harness is added to the `repo-loader` project. You can run the tests by executing the command `tox` in your terminal.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
