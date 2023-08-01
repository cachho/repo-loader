# repo-loader

This is a fork of the very excellent [gptrepo](https://github.com/zackees/gptrepo) by zackees, which itself is a fork of [gpt-repository-loader](https://github.com/mpoon/gpt-repository-loader) by mpoon.

Usage

```python
pip install repo-loader
repo-loader  # now output.txt should appear in the current directory
```

This tool concatenates through all the files in the repo and adds ai prompts which can be used for chat gpt conversations.

Simply open up the file, copy and paste it into the chat gpt window and then ask your question about the code.

This will be particularly useful when chat gpt4-32k is released. Right now this will only work on very small repos.

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

`repo-loader` is a command-line tool that converts the contents of a Git repository into a text format, preserving the structure of the files and file contents. The generated output can be interpreted by AI language models, allowing them to process the repository's contents for various tasks, such as code review or documentation generation.

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

## Versions

- 1.0.3: Remove media files from concatenation.
