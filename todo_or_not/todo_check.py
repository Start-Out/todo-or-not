import os
import json
import hashlib
import subprocess
import sys

from typer import Option, run
from typing import List, Optional
from typing_extensions import Annotated

from todo_or_not.localize import LOCALIZE
from todo_or_not.localize import SUPPORTED_ENCODINGS_TODOIGNORE
from todo_or_not.localize import SUPPORTED_ENCODINGS_TODO_CHECK

_project_dir = os.getcwd()
_todo_ignore_file = os.path.join(_project_dir, ".todo-ignore")

DEBUG = os.environ.get("DEBUG", False)
MAXIMUM_ISSUES_GENERATED = os.environ.get("MAXIMUM_ISSUES_GENERATED", 8)
PERTINENT_LINE_LIMIT = os.environ.get("PERTINENT_LINE_LIMIT", 8)
REGION = os.environ.get("REGION", "en_us")

# Validate that we support the region, otherwise default to something we have
if REGION not in LOCALIZE:
    print(F"WARNING: REGION {REGION} not recognized, defaulting to en_us (sorry, reach out to us!)\n", file=sys.stderr)
    REGION = "en_us"


class Hit:
    def __init__(self, source_file: str, source_line: int, found_keys: list[str], pertinent_lines: list[str],
                 trigger_line_index: int):
        self.found_keys = found_keys
        self.source_file = source_file
        self.source_line = source_line
        self.pertinent_lines = pertinent_lines
        self.trigger_line_index = trigger_line_index

        self.structured_title = None
        self.structured_body = None
        self.structured_labels = None

        # If this is a structured comment, parse out the title, body, and labels
        if "|" in self.pertinent_lines[trigger_line_index]:
            head, body = self.pertinent_lines[trigger_line_index].split("|", 1)

            self.structured_title = head.strip()
            self.structured_body = body.strip()

            # If there is an # in the body, there may be labels to find
            if "#" in self.structured_body:
                self.structured_labels = []

                _potential_tags = self.structured_body.split("#")

                # Skip the first item in this list, because the labels will come after the #
                for _potential in _potential_tags[1:]:
                    _label = _potential.split(" ", 1)[0]

                    if len(_label) > 0:
                        self.structured_labels.append(_label)

                if len(self.structured_labels) == 0:
                    self.structured_labels = None

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

    def get_title(self):
        return self.generic_title() if self.structured_title is None else self.structured_title

    def generic_title(self):
        return f"{self.get_found_keys()} - {self.get_triggering_line()}"

    def generate_issue(self):
        repo_uri = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}"

        github_ref = "reference"
        triggered_by = "octocat"
        owner, repo = "owner", "repository"

        if not DEBUG:
            github_ref = os.environ.get("GITHUB_REF_NAME")
            triggered_by = os.environ.get("GITHUB_TRIGGERING_ACTOR")
            owner, repo = os.environ.get('GITHUB_REPOSITORY').split("/")

        reference_file = self.source_file.split(":")[0]

        reference_uri = f"{repo_uri}/blob/{github_ref}/{reference_file}"

        body = (
            f"## {self if self.structured_body is None else self.structured_body}\n\n"
            f"{self.get_pertinent_lines()}\n\n"
            f"{LOCALIZE[REGION]['issue_body_reference_link']}: <a href=\"{reference_uri}\">{self.source_file}</a>"
        )

        api_call = [
            "gh", "api",
            "--method", "POST",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues",
            "-f", f"title={self.get_title()}",
            "-f", f"body={body}",
            "-f", f"assignees[]={triggered_by}"
        ]

        if self.structured_labels is not None:
            for label in self.structured_labels:
                api_call.append("-f")
                api_call.append(f"labels[]={label}")

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


def find_lines(filename: str, ignore_flag: str, *args) -> tuple[list[Hit], str or None]:
    """
    Finds and returns each line of a file that contains a key
    :param ignore_flag: The flag which, when detected on a triggering line, will ignore that line
    :param filename: File to open() read-only
    :param args: Keys to check each line for
    :return:
     | List of lines of text and their line number that contain at least one key and the keys each contains
     | The detected encoding of the file or none if not found
    """
    output = []

    use_encoding = get_encoding(filename, SUPPORTED_ENCODINGS_TODO_CHECK)

    if use_encoding is not None:
        with open(filename, 'r', encoding=use_encoding) as file:
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
                    while abs(line_number - _i) <= PERTINENT_LINE_LIMIT and _i >= 0:
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
                        if _i < len(lines) and len(lines[_i].strip()) > 0:
                            _pertinent_lines.append(lines[_i])
                        else:
                            # Stop when you reach a line break
                            break
                        _i += 1

                    _hit = Hit(os.path.relpath(filename, _project_dir), line_number, _found_keys, _pertinent_lines,
                               _trigger_line)
                    output.append(_hit)

                line_number += 1
    else:
        print(LOCALIZE[REGION]["warning_encoding_not_supported"], "\n * ", filename, file=sys.stderr)

    return output, use_encoding


def paste_contents_into_file(other_file_names: list[str], target_file: str):
    """
    Writes the contents of other files to the target file
    :param other_file_names: a list of path-likes pointing to source files
    :param target_file: path-like pointing to the destination file
    """

    target_file.write('\n')
    for file_name in other_file_names:
        with open(file_name, "r") as file:
            target_file.writelines(file.read())

    target_file.write('\n')


def get_bot_submitted_issues() -> list[dict]:
    """
    Makes a gh cli request for all issues submitted by app/todo-or-not, parses them, and returns them as a
    list of dicts
    :return: List of issues as dicts
    """
    owner, repo = "owner", "repository"

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

    return json.loads(_str)


def get_encoding(_target_path: str, _supported_encodings: list[str]) -> str or None:
    """
    :param _target_path: A path-like string pointing to the file for which we want to get a valid encoding
    :param _supported_encodings: A list of supported encodings e.g. `['utf-8', 'iso-8859-1', 'iso']`
    :return: The encoding of the target file if found, None if no supported encoding could be found
    """
    try:
        assert os.path.isfile(_target_path)
    except AssertionError:
        print(f"{LOCALIZE[REGION]['error_is_not_file']}: {_target_path}", file=sys.stderr)
        return None

    # Try to read the file in a supported encoding
    _use_encoding = None
    for encoding in _supported_encodings:
        try:
            with open(_target_path, 'r', encoding=encoding) as _ignore:
                _ignore.readline()
        except UnicodeDecodeError:
            # Try the next encoding without setting the used encoding
            continue
        except UnicodeError:
            # Try the next encoding without setting the used encoding
            continue

        # If able to open, use this encoding and exit the search for valid encoding
        _use_encoding = encoding
        break

    return _use_encoding


def main(
        mode: str = "print",
        silent: bool = False,
        force: bool = False,
        ni: Annotated[
            Optional[List[str]], Option(help="Copy the contents of other files into a new .todo-ignore")] = None,
        xi: Annotated[
            Optional[List[str]], Option(help="Copy the contents of other files into an existing .todo-ignore")] = None
):
    mode = mode.lower()

    targets = []
    ignored_files = []
    ignored_dirs = []

    #############################################
    # Handle settings
    #############################################

    # Don't allow the use of ni and ci at the same time
    if (len(ni) > 0) and (len(xi) > 0):
        print(LOCALIZE[REGION]['error_cannot_specify_ni_xi'], file=sys.stderr)
        exit(1)
    # If using either ni or ci...
    elif (len(ni) > 0) or (len(xi) > 0):
        # ...check if force is used and warn the user if so
        if force:
            # Check which mode is being used
            _option = "--ni" if (len(ni) > len(xi)) else "--xi"
            print(LOCALIZE[REGION]['warning_force_overrides_ignore'],
                  _option,
                  file=sys.stderr)

        # Update .todo-ignore appropriately by mode
        mode = "w" if (len(ni) > len(xi)) else "a+"
        _list = ni if (len(ni) > len(xi)) else xi

        with open(os.path.join(_project_dir, ".todo-ignore"), mode, encoding="UTF-8") as new_todo_ignore_file:
            paste_contents_into_file(_list, new_todo_ignore_file)

    #############################################
    # Parse .todo-ignore
    #############################################

    # As long as we aren't foregoing the .todo-ignore...
    if not force:
        # Unless --force is specified, a .todo-ignore in a supported encoding must be located at the project's top level
        use_encoding = get_encoding(_todo_ignore_file, SUPPORTED_ENCODINGS_TODOIGNORE)

        # If we weren't able to find a file in a supported encoding, program must exit
        if use_encoding is None:
            print(LOCALIZE[REGION]['error_todo_ignore_not_supported'], file=sys.stderr)
            exit(1)

        # ... actually do the reading of the .todo-ignore
        with open(_todo_ignore_file, 'r', encoding=use_encoding) as _ignore:
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

            if len(ignored_files) == 0 and len(ignored_dirs) == 0:
                print(LOCALIZE[REGION]['warning_run_with_empty_todo_ignore'], file=sys.stderr)

            # Ignore the .todo-ignore itself
            ignored_files.append(os.path.abspath(_ignore.name))
    else:
        print(f"{LOCALIZE[REGION]['error_todo_ignore_not_found']}[{LOCALIZE['windows']['shell_sigint']}]",
              file=sys.stderr)

    #############################################
    # Collect files to scan
    #############################################

    # Ignore this script
    ignored_files.append(__file__)

    _walk = os.walk(_project_dir, topdown=True)

    for (dirpath, dirnames, filenames) in _walk:
        _to_remove = []

        # Find all ignored dirs from this step of the walk
        for dirname in dirnames:
            for _dir in ignored_dirs:
                _dirname = os.path.join(dirpath, dirname)
                if os.path.samefile(_dirname, _dir):
                    # Found this directory in the ignored directories, mark for removal and move to the next
                    _to_remove.append(dirname)
                    break

        # Remove those directories (can't do in place because indexing)
        for remove in _to_remove:
            dirnames.remove(remove)

        for _file in filenames:
            current = os.path.join(dirpath, _file)

            for i in ignored_files:
                if os.path.samefile(i, current):
                    current = None
                    break

            if current is not None:
                targets.append(current)

    #############################################
    # Preventing duplicate issues
    #############################################

    # When pinging for all queries, their titles are hashed and saved here. This is for checking for duplicate issues
    existing_issues_hashed = []

    # Collect all the issues that the bot has so far submitted to check for duplicates
    if mode == "issue":
        todoon_created_issues = get_bot_submitted_issues()

        for issue in todoon_created_issues:
            existing_issues_hashed.append(_hash(issue["title"]))

    #############################################
    # Run todo-check
    #############################################

    number_of_hits = 0  # Tracks the number of targets found
    number_of_issues = 0  # Tracks the number of issues generated
    number_of_encoding_failures = 0  # Tracks the files unread due to encoding error

    # Used for summary
    number_of_todo, number_of_fixme = 0, 0

    # For each target file discovered
    for target in targets:
        # Generate the hits for each target collected
        hits, _enc = find_lines(target, "#todoon", "todo", "fixme")

        if _enc is None:
            number_of_encoding_failures += 1

        # If any hits were detected...
        if len(hits) > 0:

            # Handle each hit that was detected
            for hit in hits:
                number_of_hits += 1
                number_of_todo += 1 if "todo" in hit.found_keys else 0
                number_of_fixme += 1 if "fixme" in hit.found_keys else 0

                #############################################
                # Special handling for the ISSUE mode

                if mode == "issue":
                    _this_hit_hashed = _hash(hit.get_title())

                    # Check if the app already created this hit's title
                    if _this_hit_hashed not in existing_issues_hashed:

                        # Limit the number of issues created in one run
                        if number_of_issues < MAXIMUM_ISSUES_GENERATED:
                            hit.generate_issue()
                            number_of_issues += 1
                        else:
                            print(LOCALIZE[REGION]['error_todo_ignore_not_found'], file=sys.stderr)
                            exit(1)
                    # If this title already exists, notify but do not halt
                    else:
                        print(f"{LOCALIZE[REGION]['info_duplicate_issue_avoided']}: {hit}", file=sys.stderr)

                #############################################
                # If not in ISSUE mode, print hit to stderr

                else:
                    print(hit, file=sys.stderr)

    #############################################
    # Summarize the run of todo-check
    #############################################

    summary = f"\n##########################\n# {LOCALIZE[REGION]['summary_title']}\n"
    summary += f"# {number_of_todo} TODO | {number_of_fixme} FIXME\n"

    if number_of_encoding_failures > 1:
        summary += f"# {number_of_encoding_failures} {LOCALIZE[REGION]['summary_encoding_unsupported_plural']}\n"
    elif number_of_encoding_failures == 1:
        summary += f"# {number_of_encoding_failures} {LOCALIZE[REGION]['summary_encoding_unsupported_singular']}\n"

    summary += f"# ({mode.upper()} MODE)\n"
    summary += "##########################\n"

    print(summary, file=sys.stderr)

    # Fail if any hits were found and we are not in silent mode
    if number_of_hits > 0 and not silent:
        exit(1)


def typer_main():
    run(main)


if __name__ == "__main__":
    typer_main()
