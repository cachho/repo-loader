#!/usr/bin/env python3

import argparse
import os
import sys
from typing import Optional

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


def process_repository(repo_path, ignore_list, output_file, use_progress_bar, is_quiet):
    """Main function to iterate through the repository and write to the outfile."""
    # pylint: disable=fixme
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
            # pylint: disable=consider-using-generator
            num_files = sum([len(files) for r, d, files in os.walk(content_path)])
            if num_files == 0:
                continue

            if not is_quiet and not use_progress_bar:
                print(f"Processing directory: {content}")

            pbar = (
                tqdm(
                    total=num_files, bar_format="{l_bar}{bar:50}{r_bar}", desc=f"{content[:17]:<20}"
                )
                if use_progress_bar
                else None
            )

            for root, _, files in os.walk(content_path):
                for file in files:
                    process_file(root, file, repo_path, ignore_list, output_file)
                    if pbar:
                        pbar.update(1)

            if pbar:
                pbar.close()

        else:
            # It is a file
            if not is_quiet and not use_progress_bar:
                print(f"Processing file: {content}")
            process_file(repo_path, content, repo_path, ignore_list, output_file)


def process_file(root, file, repo_path, ignore_list, output_file):
    """Write file content to output file"""
    file_path = os.path.join(root, file)
    relative_file_path = os.path.relpath(file_path, repo_path)

    if not should_ignore(relative_file_path, ignore_list):
        with open(file_path, "r", errors="ignore") as f:
            contents = f.read()

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

    if not os.path.exists(ignore_file_path):
        # try and use the .gptignore file in the current directory as a fallback.
        ignore_file_path = os.path.join(HERE, filename)
        try:
            assert os.path.exists(ignore_file_path)
            with open(ignore_file_path, "r") as ignore_file:
                contents = ignore_file.read()
            with open(ignore_file_path, "w") as ignore_file:
                ignore_file.write(contents)
        except AssertionError:
            # if the fallback file doesn't exist either, return empty list.
            return []

    ignore_list = []
    # Check ignore_file_path again
    if os.path.exists(ignore_file_path):
        # Add lines to ignore_list
        with open(ignore_file_path, "r") as ignore_file:
            for line in ignore_file:
                ignore_list.append(line.strip())
    return ignore_list


# pylint: disable=too-many-arguments
def load(
    repo_path: Optional[str] = None,
    out_path: Optional[str] = None,
    preamble_file: Optional[str] = None,
    clipboard: bool = False,
    quiet: bool = False,
    progress: bool = False,
    open_file_after_processing: bool = False,
):
    """
    Processes a git repository into a single text file.

    Args:
        repo_path (str, optional): The path to the git repository to be processed.
                                   Defaults to the current working directory if None.
        out_path (str, optional): The path to the output file.
                                  Defaults to 'output.txt' if None.
        preamble_file (str, optional): The path to a preamble file. The contents of this
                                       file will be written to the output file before the
                                       repository contents. If None, no preamble is used.
        clipboard (bool, optional): If True, the contents of the output file will be
                                     copied to the clipboard instead of written to a file.
                                     Defaults to False.
        quiet (bool, optional): If True, the script will not print to stdout
                                and will not automatically open the output file.
                                Defaults to False.
        progress (bool, optional): If True, the script will display a progress
                                   bar while processing the repository.
                                   Defaults to False.
        open_file_after_processing (bool, optional): If True, the output file will be
                                                     automatically opened after processing.
                                                     Defaults to False.
    """

    # Set defaults
    repo_path = repo_path or os.getcwd()
    out_path = out_path or "output.txt"

    gpt_ignore_list = build_ignore_list(repo_path=repo_path, filename=".gptignore")
    git_ignore_list = build_ignore_list(repo_path=repo_path, filename=".gitignore")

    ignore_list = gpt_ignore_list + git_ignore_list + [out_path]
    ignore_list = [x for x in ignore_list if x and len(x) > 0 and x[0] != "#"]
    ignore_list = list(set(ignore_list))

    outfile = os.path.abspath(out_path)
    with open(outfile, "w") as output_file:
        if preamble_file:
            with open(preamble_file, "r") as pf:
                preamble_text = pf.read()
                output_file.write(f"{preamble_text}\n")
        else:
            output_file.write("The following text is a Git repository with code. ...")
        process_repository(repo_path, ignore_list, output_file, progress, quiet)
    with open(out_path, "a") as output_file:
        output_file.write("--END--")

    if not clipboard:
        if not quiet:
            print(f"Repository contents written to {out_path}")
        if open_file_after_processing:
            open_file(filename=out_path)
    if clipboard:
        with open(out_path, "r") as output_file:
            contents = output_file.read()
        pyperclip.copy(contents)
        os.remove(out_path)
        if not quiet:
            print("Copied to clipboard")


def main() -> int:
    """
    Processes a git repository into a single text file. The script is
    intended to be used from the command line, and has several options
    for customizing its behavior.

    Command Line Arguments:
        repo_path: The path to the git repository that should be processed.
                   If this argument is omitted, the current working directory is used.
        -o, --output: The path to the output file. If omitted, output.txt will be used.
        -p, --preamble: The path to a preamble file. The contents of this file
                        will be written to the output file before the repository contents.
        --clipboard: If this flag is present, the contents of the output file
                     will be copied to the clipboard instead of written to a file.
        -q, --quiet: If this flag is present, the script will not print to stdout
                     and will not automatically open the output file.
        -pg, --progress: If this flag is present, the script will display a progress
                         bar while processing the repository.
        --open: If this flag is present, the output file will be automatically
                opened after processing.
        --write-config: Writes a default config file to the target directory.
                        If a directory is specified, the config file will be written there.
                        If no directory is specified, the config file will be written
                        to the current working directory.
    """
    # copy this but using argparse
    parser = argparse.ArgumentParser(
        description="Process a git repository into a single file for chat gpt."
    )
    parser.add_argument("repo_path", help="path to the git repository", type=str, nargs="?")
    parser.add_argument("-o", "--output", help="output file path", type=str, nargs="?")
    parser.add_argument("-p", "--preamble", help="path to the preamble file", type=str, nargs="?")
    parser.add_argument("--clipboard", help="copy the output to the clipboard", action="store_true")
    parser.add_argument("-q", "--quiet", help="no stdout, file not opened", action="store_true")
    parser.add_argument("-pg", "--progress", help="display a progress bar", action="store_true")
    parser.add_argument("--open", help="open file after processing", action="store_true")
    parser.add_argument(
        "--write-config",
        help="Write a default config file to the target directory.",
        type=str,
        nargs="?",
    )
    args = parser.parse_args()

    load(
        repo_path=args.repo_path,
        out_path=args.output,
        preamble_file=args.preamble,
        clipboard=args.clipboard,
        quiet=args.quiet,
        progress=args.progress,
        open_file_after_processing=args.open,
    )
    return 0
