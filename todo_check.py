import os
import json
import hashlib
import subprocess
import sys

from typer import Option, run
from typing import List, Optional
from typing_extensions import Annotated

_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_dir = _script_dir
_todo_ignore_file = os.path.join(_project_dir, ".todo-ignore")

DEBUG = os.environ.get("DEBUG", False)
MAXIMUM_ISSUES_GENERATED = os.environ.get("MAXIMUM_ISSUES_GENERATED", 8)
PERTINENT_LINE_LIMIT = os.environ.get("PERTINENT_LINE_LIMIT", 8)


class Hit:
    def __init__(self, source_file: str, source_line: int, found_keys: list[str], pertinent_lines: list[str],
                 trigger_line_index: int):
        self.found_keys = found_keys
        self.source_file = source_file
        self.source_line = source_line
        self.pertinent_lines = pertinent_lines
        self.trigger_line_index = trigger_line_index

    def __repr__(self):
        _line = self.get_triggering_line()
        _line_number = self.get_line_number()
        _found_keys = self.get_found_keys()

        header = f"[{self.get_found_keys()}]"
        _pad = 16 - len(header)
        padding = " " * _pad
        header = header + padding

        location = os.path.relpath(self.source_file, _project_dir)
        location = f"{location}:{_line_number}"
        _pad = 16 - len(location)
        padding = " " * _pad
        location = location + padding

        return f"{header} - {location} - {_line.strip()}"

    def get_triggering_line(self):
        return self.pertinent_lines[self.trigger_line_index]

    def get_line_number(self):
        return self.source_line

    def get_found_keys(self):
        return ", ".join(self.found_keys).upper()

    def get_file_extension(self):
        return self.source_file.split(".")[-1:][0]

    def get_pertinent_lines(self):
        starting_line_number = self.source_line - self.trigger_line_index
        _max_line = self.source_line + (len(self.pertinent_lines) - self.trigger_line_index)

        def _parse_line_number(_l: int, star: bool = False) -> str:
            _padding = len(str(_max_line))
            _padding += 3

            _decoration = "* " if star else "  "

            return f"{_decoration}{str(_l)}:".rjust(_padding, " ")

        output = f"```{self.get_file_extension()}\n"

        for pertinent_line in self.pertinent_lines:
            output += (f"{_parse_line_number(starting_line_number, starting_line_number == self.source_line)}\t"
                       f"{pertinent_line}")
            starting_line_number += 1

        output += "```"

        return output

    def generate_issue(self):
        title = f"{self.get_found_keys()} - {self.get_triggering_line()}"

        repo_uri = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}"

        github_ref = "owner/repository"
        triggered_by = "octocat"
        owner, repo = "owner", "repository"

        if not DEBUG:
            github_ref = os.environ.get('GITHUB_REF').split("/")
            triggered_by = os.environ.get("GITHUB_TRIGGERING_ACTOR")
            owner, repo = os.environ.get('GITHUB_REPOSITORY').split("/")

        reference = self.source_file.split(":")[0]

        reference_uri = f"{repo_uri}/blob/{'/'.join(github_ref[2:])}/{reference}"

        body = (
            f"## {self}\n\n"
            f"{self.get_pertinent_lines()}\n\n"
            f"Reference: <a href=\"{reference_uri}\">{self.source_file}</a>"
        )

        api_call = [
            "gh", "api",
            "--method", "POST",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues",
            "-f", f"title={title}",
            "-f", f"body={body}",
            "-f", f"assignees[]={triggered_by}"
        ]

        if not DEBUG:
            _output = subprocess.check_output(api_call)
        else:
            _output = "DEBUGGING"
            print(api_call)

        return _output


def _hash(hit_str: str):
    m = hashlib.sha1()
    m.update(bytes(hit_str, "utf-8"))
    return m.hexdigest()


def find_lines(filename: str, ignore_flag: str, *args) -> list[Hit]:
    """
    Finds and returns each line of a file that contains a key
    :param ignore_flag: The flag which, when detected on a triggering line, will ignore that line
    :param filename: File to open() read-only
    :param args: Keys to check each line for
    :return: List of lines of text and their line number that contain at least one key and the keys each contains
    """
    output = []

    with open(filename, 'r', encoding="UTF-8") as file:
        line_number = 1
        lines = file.readlines()

        for _line in lines:
            _found_keys = []
            for key in args:
                if key.lower() in _line.lower() and ignore_flag.lower() not in _line.lower():
                    _found_keys.append(key)

            if len(_found_keys) > 0:
                # Collect surrounding lines that may be pertinent
                _pertinent_lines = []

                # Look at lines before the pertinent line
                _i = line_number - 1
                while abs(line_number - _i) <= PERTINENT_LINE_LIMIT:
                    _i -= 1
                    if len(lines[_i].strip()) > 0:
                        _pertinent_lines.insert(0, lines[_i])
                    else:
                        # Stop when you reach a line break
                        break

                # Push the triggering line to the pertinent lines and note its index
                _trigger_line = len(_pertinent_lines)
                _pertinent_lines.append(lines[line_number - 1])

                # Look at lines after the pertinent line
                _i = line_number
                while abs(_i - line_number) <= PERTINENT_LINE_LIMIT:
                    if len(lines[_i].strip()) > 0:
                        _pertinent_lines.append(lines[_i])
                    else:
                        # Stop when you reach a line break
                        break
                    _i += 1

                _hit = Hit(filename, line_number, _found_keys, _pertinent_lines, _trigger_line)
                output.append(_hit)

            line_number += 1

    return output


def update_todo_ignore(other_file_names, target_file):
    target_file.write('\n')
    for file_name in other_file_names:
        with open(file_name, "r") as file:
            target_file.writelines(file.read())


def get_issues():
    owner, repo = "start-out", "todo-or-not"

    if not DEBUG:
        owner, repo = os.environ.get('GITHUB_REPOSITORY').split("/")

    response = subprocess.check_output(
        [
            "gh", "api",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues?creator=app%2Ftodo-or-not"
        ]
    )

    _str = response.decode("utf-8")
    _str.replace("\"", '\\\"')
    # _str.replace("'", '"')
    # return _str

    return json.loads(_str)

def main(
        mode: str = "print",
        silent: bool = False,
        force: bool = False,
        ni: Annotated[
            Optional[List[str]], Option(help="Copy the contents of other files into a new .todo-ignore")] = None,
        xi: Annotated[
            Optional[List[str]], Option(help="Copy the contents of other files into an existing .todo-ignore")] = None
):
    targets = []
    ignored_files = []
    ignored_dirs = []

    if (len(ni) > 0) and (len(xi) > 0):
        print("FATAL: Cannot specify both --ni and --ci.", file=sys.stderr)
        exit(1)
    elif (len(ni) > 0) or (len(xi) > 0):
        if force:
            _option = "--ni" if (len(ni) > len(xi)) else "--ci"
            print("WARNING: --force will ignore the contents of the .todo-ignore generated when you specified",
                  _option,
                  file=sys.stderr)

        mode = "a+" if (len(ni) > len(xi)) else "w"
        _list = ni if (len(ni) > len(xi)) else xi

        with open(os.path.join(_project_dir, ".todo-ignore"), mode, encoding="UTF-8") as new_todo_ignore_file:
            update_todo_ignore(_list, new_todo_ignore_file)

    if not force:
        try:
            with open(_todo_ignore_file, 'r'):
                pass
        except FileNotFoundError:
            print(
                "FATAL: .todo-ignore NOT FOUND! use -i to copy another .ignore OR "
                "--force to run without a .todo-ignore (NOT RECOMMENDED)",
                file=sys.stderr)
            exit(1)

        with open(_todo_ignore_file, 'r') as _ignore:
            for line in _ignore.readlines():
                if not line.startswith("#") and len(line) > 1:
                    if line.endswith('\n'):
                        cur_name = line[:-1]
                    else:
                        cur_name = line

                    cur_path = os.path.join(_project_dir, cur_name)

                    if os.path.isfile(cur_path):
                        ignored_files.append(cur_path)

                    if os.path.isdir(cur_path):
                        ignored_dirs.append(cur_path)

            # Ignore the .todo-ignore itself
            ignored_files.append(os.path.abspath(_ignore.name))
    else:
        print("WARNING: Running without a .todo-ignore (NOT RECOMMENDED), [Ctrl + C] to cancel", file=sys.stderr)

    # Ignore this script
    ignored_files.append(__file__)

    _walk = os.walk(_project_dir)

    for (dirpath, dirnames, filenames) in _walk:
        # Break if an ignored dir
        _ignore_this_dir = False

        for _dir in ignored_dirs:
            if os.path.samefile(dirpath, _dir):
                _ignore_this_dir = True
        if _ignore_this_dir:
            break

        for _file in filenames:
            current = os.path.join(dirpath, _file)

            for i in ignored_files:
                if os.path.samefile(i, current):
                    current = None
                    break

            if current is not None:
                targets.append(current)

    #############################################
    # Handle output
    #############################################

    existing_issues_hashed = []

    if mode.lower() == "issue":
        todoon_created_issues = get_issues()

        for issue in todoon_created_issues:
            existing_issues_hashed.append(_hash(issue["title"]))

        print(existing_issues_hashed)

    fail = False
    number_of_hits = 0
    for target in targets:
        # Generate the hits for each target collected
        hits = find_lines(target, "#todoon", "todo", "fixme")

        if len(hits) > 0:
            fail = True

            # Print the hits if the issue option is not specified, if it is then be silent and generate issues
            # _printable_hits = _print_todo_found(target, hits, mode.lower() == "issue")

            for hit in hits:
                if mode.lower() == "issue":
                    number_of_hits += 1

                    if number_of_hits < MAXIMUM_ISSUES_GENERATED:
                        hit.generate_issue()
                    else:
                        print("FATAL: Exceeded maximum number of issues for this run, exiting now", file=sys.stderr)
                        exit(1)
                else:
                    print(hit, file=sys.stderr)

    if fail:
        print(
            f"\n######\nTODO and FIXME check failed, please address the issues and try again. "
            f"(mode is {mode.upper()})\n######\n")
        if not silent:
            exit(1)
    else:
        print("\n######\nTODO and FIXME check complete.\n######\n")


if __name__ == "__main__":
    run(main)
