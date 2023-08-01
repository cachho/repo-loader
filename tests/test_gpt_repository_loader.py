import os
import shutil
import tempfile
import unittest

from repo_loader.repo_loader import build_ignore_list, process_repository

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GPT_IGNORE_PATH = os.path.join(PROJECT_ROOT, "src", "repo_loader", ".gptignore")


class TestGPTRepositoryLoader(unittest.TestCase):
    def setUp(self):
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_data")
        self.example_repo_path = os.path.join(self.test_data_path, "example_repo")

    def test_end_to_end(self):
        # Set up the output file and the expected output file paths
        output_file_path = os.path.join(tempfile.mkdtemp(), "output.txt")
        expected_output_file_path = os.path.join(
            self.test_data_path, "expected_output.txt"
        )

        # Create an ignore list for the example repository
        ignore_file_path = os.path.join(self.example_repo_path, ".gptignore")
        if os.path.exists(ignore_file_path):
            ignore_list = build_ignore_list(self.example_repo_path, ".gptignore")
        else:
            ignore_list = []

        # Run the gpt-repository-loader script on the example repository
        with open(output_file_path, "w") as output_file:
            process_repository(
                self.example_repo_path,
                ignore_list,
                output_file,
                use_progress_bar=False,
                is_quiet=True,
            )

        # Compare the output to the expected output
        with open(expected_output_file_path, "r") as file:
            lines_expected = {line.replace("/", os.path.sep).rstrip() for line in file}

        with open(output_file_path, "r") as file:
            lines_actual = {line.rstrip() for line in file}

        self.assertSetEqual(lines_expected, lines_actual)

        # Clean up the output file
        shutil.rmtree(os.path.dirname(output_file_path))

    def test_gptignore(self):
        self.assertTrue(os.path.exists(GPT_IGNORE_PATH))


if __name__ == "__main__":
    unittest.main()
