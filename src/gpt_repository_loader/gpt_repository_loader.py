#!/usr/bin/env python3

import argparse
import os
import sys

import pyperclip
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from tqdm import tqdm

from .utils import is_readable

HERE = os.path.dirname(os.path.abspath(__file__))


def open_file(filename):
    """Open the outfile in a OS-specific reader"""
    if sys.platform == "win32":
        os.startfile(filename)
    elif sys.platform == "darwin":
        os.system(f"open {filename}")
    else:
        try:
            os.system(f"xdg-open {filename}")
        except Exception:  # pylint: disable=broad-except
            pass


def should_ignore(file_path, ignore_patterns):
    """Determines whether a file should be ignored, based on the ignore patterns."""
    spec = PathSpec.from_lines(GitWildMatchPattern, ignore_patterns)
    return spec.match_file(file_path)


def process_repository(repo_path, ignore_list, output_file):
    """Main function to iterate through the repository and write to the outfile."""
    # TODO: This could be optimized, by skipping a directory that's ignored,
    # if the whole directory is ignored. For instance right now it will go through 
    # all files in `venv` and determine that each is ignored, instead of just skipping
    # the whole directory
    # Get a list of top-level files and directories.
    top_level_contents = list(os.listdir(repo_path))

    for content in top_level_contents:
        content_path = os.path.join(repo_path, content)
        
        # Check if it is a file or directory
        if os.path.isdir(content_path):
            # It is a directory
            
            # Count the number of files in the directory (including all subdirectories).
            num_files = sum([len(files) for r, d, files in os.walk(content_path)])
            if num_files == 0:
                continue

            print(f"Processing directory: {content}")

            with tqdm(total=num_files, bar_format='{l_bar}{bar:50}{r_bar}') as pbar:
                for root, _, files in os.walk(content_path):
                    for file in files:
                        process_file(root, file, repo_path, ignore_list, output_file)
                        pbar.update(1)
        else:
            # It is a file
            print(f"Processing file: {content}")
            process_file(repo_path, content, repo_path, ignore_list, output_file)

def process_file(root, file, repo_path, ignore_list, output_file):
    file_path = os.path.join(root, file)
    relative_file_path = os.path.relpath(file_path, repo_path)

    if not should_ignore(relative_file_path, ignore_list):
        with open(file_path, "r", errors="ignore") as file:
            contents = file.read()

            if len(contents) == 0:
                # Ignore empty files
                return

            if not is_readable(contents):
                # Ignore binary files
                return

        output_file.write("----!@#$----" + "\n")
        output_file.write(f"{relative_file_path}\n")
        output_file.write(f"{contents}\n")


def build_ignore_list(repo_path, filename):
    """Read ignore file by filename and build ignore list"""
    ignore_file_path = os.path.join(repo_path, filename)
    if sys.platform == "win32":
        ignore_file_path = ignore_file_path.replace("/", "\\")

    if not os.path.exists(ignore_file_path):
        # try and use the .gptignore file in the current directory as a fallback.
        ignore_file_path = os.path.join(HERE, filename)
        assert os.path.exists(ignore_file_path)
        with open(ignore_file_path, "r") as ignore_file:
            contents = ignore_file.read()
        with open(ignore_file_path, "w") as ignore_file:
            ignore_file.write(contents)

    ignore_list = []
    # Check ignore_file_path again
    if os.path.exists(ignore_file_path):
        # Add lines to ignore_list
        with open(ignore_file_path, "r") as ignore_file:
            for line in ignore_file:
                if sys.platform == "win32":
                    line = line.replace("/", "\\")
                ignore_list.append(line.strip())
    return ignore_list


def main() -> int:  # pylint: disable=too-many-statements
    # copy this but using argparse
    parser = argparse.ArgumentParser(
        description="Process a git repository into a single file for chat gpt."
    )
    parser.add_argument("repo_path", help="path to the git repository", type=str, nargs="?")
    parser.add_argument("-o", "--output", help="output file path", type=str, nargs="?")
    parser.add_argument("-p", "--preamble", help="path to the preamble file", type=str, nargs="?")
    parser.add_argument("--clipboard", help="copy the output to the clipboard", action="store_true")
    parser.add_argument("-q", "--quiet", help="no stdout, file not opened", action="store_true")
    parser.add_argument(
        "--write-config",
        help="Write a default config file to the target directory.",
        type=str,
        nargs="?",
    )
    args = parser.parse_args()

    repo_path = args.repo_path or os.getcwd()
    out_path = args.output or "output.txt"

    gpt_ignore_list = build_ignore_list(repo_path=repo_path, filename=".gptignore")
    git_ignore_list = build_ignore_list(repo_path=repo_path, filename=".gitignore")

    # TODO: Added `output.txt` to gitignore, otherwise it keeps adding itself.
    # There might be a better way to do this, in case there is a file with the same name you want to add.
    ignore_list = gpt_ignore_list + git_ignore_list + [out_path]
    # Filter comments and empty lines
    ignore_list = [x for x in ignore_list if len(x) > 0 and x[0] != '#']
    # Filter duplicats
    ignore_list = list(set(ignore_list))

    preamble_file = args.preamble

    outfile = os.path.abspath(out_path)
    with open(outfile, "w") as output_file:
        if preamble_file:
            with open(preamble_file, "r") as pf:
                preamble_text = pf.read()
                output_file.write(f"{preamble_text}\n")
        else:
            output_file.write(
                "The following text is a Git repository with code. The structure of the text are sections that begin with ----!@#$----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n"
            )
        process_repository(repo_path, ignore_list, output_file)
    with open(out_path, "a") as output_file:
        output_file.write("--END--")
    if not args.clipboard and not args.quiet:
        print(f"Repository contents written to {out_path}")
        open_file(filename=out_path)
        return 0
    if args.clipboard:
        with open(out_path, "r") as output_file:
            contents = output_file.read()
        pyperclip.copy(contents)
        os.remove(out_path)
        if not (args.quiet):
            print("Copied to clipboard")
    return 0
