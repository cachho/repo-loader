import os
import shutil
import tempfile
import unittest

from gpt_repository_loader.gpt_repository_loader import (
    get_ignore_list,
    process_repository,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GPT_IGNORE_PATH = os.path.join(
    PROJECT_ROOT, "src", "gpt_repository_loader", ".gptignore"
)


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
            ignore_list = get_ignore_list(ignore_file_path)
        else:
            ignore_list = []

        # Run the gpt-repository-loader script on the example repository
        with open(output_file_path, "w") as output_file:
            process_repository(self.example_repo_path, ignore_list, output_file)

        # Compare the output to the expected output

        lines_expected = open(  # pylint: disable=consider-using-with
            expected_output_file_path
        ).readlines()
        lines_actual = open(
            output_file_path
        ).readlines()  # pylint: disable=consider-using-with

        self.assertEqual(len(lines_expected), len(lines_actual))
        for i in range(len(lines_expected)):  # pylint: disable=consider-using-enumerate
            self.assertEqual(
                lines_expected[i].replace("/", os.path.sep), lines_actual[i]
            )

        # Clean up the output file
        shutil.rmtree(os.path.dirname(output_file_path))

    def test_gptignore(self):
        self.assertTrue(os.path.exists(GPT_IGNORE_PATH))


if __name__ == "__main__":
    unittest.main()
