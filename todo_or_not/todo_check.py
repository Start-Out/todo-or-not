import glob
import os
import json
import hashlib
import subprocess
import sys

from pathlib import Path
import typer
from typer import Option, run
from typing import List, Optional, TextIO
from typing_extensions import Annotated

from todo_or_not.localize import LOCALIZE  # todoon
from todo_or_not.localize import SUPPORTED_ENCODINGS_TODOIGNORE  # todoon
from todo_or_not.localize import SUPPORTED_ENCODINGS_TODO_CHECK  # todoon


todoon_app = typer.Typer(name="todoon")  # todoon


def get_project_dir():
    return os.getcwd()


def get_todo_ignore_path():  # todoon
    return os.path.join(get_project_dir(), ".todo-ignore")  # todoon


def get_is_debug():
    _debug = os.environ.get("DEBUG", "False")
    if _debug == "True":
        return True
    else:
        return False


def get_max_issues():
    _max_issues = os.environ.get("MAXIMUM_ISSUES_GENERATED", "8")

    try:
        max_issues = int(_max_issues)
    except:
        max_issues = 8

    return max_issues


def get_pertinent_line_limit():
    _pertinent_line_limit = os.environ.get("PERTINENT_LINE_LIMIT", "8")

    try:
        pertinent_line_limit = int(_pertinent_line_limit)
    except:
        pertinent_line_limit = 8

    return pertinent_line_limit


def get_region():
    region = os.environ.get("REGION", "en_us")

    # Validate that we support the region, otherwise default to something we have
    if region not in LOCALIZE:
        print(
            LOCALIZE["en_us"]["warning_using_default_region"],
            region,
            file=sys.stderr,
        )
        region = "en_us"

    return region


def get_os():
    _os = os.environ.get("OS", "default")
    _os = _os.lower()

    # Validate that we support the region, otherwise default to something we have
    if _os not in LOCALIZE:
        print(
            LOCALIZE[get_region()]["warning_using_default_os"],
            _os,
            file=sys.stderr,
        )
        _os = "default"

    return _os


class Hit:
    def __init__(
            self,
            source_file: str,
            source_line: int,
            found_keys: list[str],
            pertinent_lines: list[str],
            trigger_line_index: int,
    ):
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

        if self.structured_title is not None:
            return self.structured_title

        _line = self.get_triggering_line()
        _line_number = self.get_line_number()
        _found_keys = self.get_found_keys()

        header = f"[{self.get_found_keys()}]"
        _pad = 16 - len(header)
        padding = " " * _pad
        header = header + padding

        location = os.path.relpath(self.source_file, get_project_dir())
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
        _max_line = self.source_line + (
                len(self.pertinent_lines) - self.trigger_line_index
        )

        def _parse_line_number(_l: int, star: bool = False) -> str:
            _padding = len(str(_max_line))
            _padding += 3

            _decoration = "* " if star else "  "

            return f"{_decoration}{str(_l)}:".rjust(_padding, " ")

        output = f"```{self.get_file_extension()}\n"

        for pertinent_line in self.pertinent_lines:
            output += (
                f"{_parse_line_number(starting_line_number, starting_line_number == self.source_line)}\t"
                f"{pertinent_line}"
            )
            starting_line_number += 1

        output += "```"

        return output

    def get_title(self):
        return (
            self.generic_title()
            if self.structured_title is None
            else self.structured_title
        )

    def generic_title(self):
        return f"{self.get_found_keys()} - {self.get_triggering_line()}"

    def generate_issue(self, _test: bool = False) -> str or bool:

        repo_uri = f"https://github.com/None"

        github_ref = "$NONE"
        triggered_by = "$NONE"
        owner, repo = "$NONE", "$NONE"

        if not (get_is_debug() or _test):
            repo_uri = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}"

            github_ref = os.environ.get("GITHUB_REF_NAME", "$NONE")
            triggered_by = os.environ.get("GITHUB_TRIGGERING_ACTOR", "$NONE")
            owner, repo = os.environ.get("GITHUB_REPOSITORY", "$NONE/$NONE").split("/")

            # Find missing env variables
            missing_envs = []

            if github_ref == "$NONE":
                print(f"{LOCALIZE[get_region()]['error_no_env']}: GITHUB_REF_NAME", file=sys.stderr)
                missing_envs.append("GITHUB_REF_NAME")
            if triggered_by == "$NONE":
                print(f"{LOCALIZE[get_region()]['error_no_env']}: GITHUB_TRIGGERING_ACTOR", file=sys.stderr)
                missing_envs.append("GITHUB_TRIGGERING_ACTOR")
            if owner == "$NONE":
                print(f"{LOCALIZE[get_region()]['error_no_env']}: GITHUB_REPOSITORY", file=sys.stderr)
                missing_envs.append("GITHUB_REPOSITORY")
            if repo == "$NONE":
                print(f"{LOCALIZE[get_region()]['error_no_env']}: GITHUB_REPOSITORY", file=sys.stderr)
                missing_envs.append("GITHUB_REPOSITORY")

            if len(missing_envs) > 0:
                return False

        reference_file = self.source_file.split(":")[0]

        reference_uri = f"{repo_uri}/blob/{github_ref}/{reference_file}"

        body = (
            f"## {self if self.structured_body is None else self.structured_body}\n\n"
            f"{self.get_pertinent_lines()}\n\n"
            f"{LOCALIZE[get_region()]['issue_body_reference_link']}: <a href=\"{reference_uri}\">{self.source_file}</a>"
        )

        # Sanitize @ to prevent abuse
        body.replace("@", "@<!-- -->")

        api_call = [
            "gh",
            "api",
            "--method",
            "POST",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues",
            "-f",
            f"title={self.get_title()}",
            "-f",
            f"body={body}",
            "-f",
            f"assignees[]={triggered_by}",
        ]

        if self.structured_labels is not None:
            for label in self.structured_labels:
                api_call.append("-f")
                api_call.append(f"labels[]={label}")

        if not (get_is_debug() or _test):
            try:
                _output = subprocess.check_output(api_call)
            except subprocess.CalledProcessError as e:
                print(e, file=sys.stderr)
                _output = False
        else:
            _output = True
            print(api_call)

        return _output


def _hash(hit_str: str):
    m = hashlib.sha1()
    m.update(bytes(hit_str, "utf-8"))
    return m.hexdigest()


def find_lines(
        filename: str, verbose: bool, ignore_flag: str, *args
) -> tuple[list[Hit], str or None]:
    """
    Finds and returns each line of a file that contains a key
    :param verbose: Print lengthy feedback which includes (encoding failures)
    :param ignore_flag: The flag which, when detected on a triggering line, will ignore that line
    :param filename: File to open() read-only
    :param args: Keys to check each line for
    :return:
     | List of lines of text and their line number that contain at least one key and the keys each contains
     | The detected encoding of the file or none if not found
    """
    output = []

    use_encoding = get_encoding(filename, SUPPORTED_ENCODINGS_TODO_CHECK)  # todoon

    if use_encoding is not None:
        with open(filename, "r", encoding=use_encoding) as file:
            line_number = 0
            lines = file.readlines()

            for _line in lines:
                line_number += 1

                # If this line contains the ignore flag, simply move on
                if ignore_flag.lower() in _line.lower():
                    continue

                # Collect the found keys and their associated info
                _found_keys = []

                for key in args:
                    if key.lower() in _line.lower():
                        _found_keys.append(key)

                if len(_found_keys) > 0:
                    # Collect surrounding lines that may be pertinent
                    _pertinent_lines = []

                    # Look at lines before the pertinent line
                    _i = line_number - 1
                    while abs(line_number - _i) <= get_pertinent_line_limit() and _i >= 0:
                        _i -= 1
                        if len(lines[_i].strip()) > 0:
                            _pertinent_lines.insert(0, lines[_i])
                        else:
                            # Stop when you reach a line break
                            break

                    # Push the triggering line to the pertinent lines and note its index
                    _pertinent_lines.append(lines[line_number - 1])
                    _trigger_line = len(_pertinent_lines) - 1

                    # Look at lines after the pertinent line
                    _i = line_number
                    while abs(_i - line_number) <= get_pertinent_line_limit():
                        if _i < len(lines) and len(lines[_i].strip()) > 0:
                            _pertinent_lines.append(lines[_i])
                        else:
                            # Stop when you reach a line break
                            break
                        _i += 1

                    _hit = Hit(
                        os.path.relpath(filename, get_project_dir()),
                        line_number,
                        _found_keys,
                        _pertinent_lines,
                        _trigger_line,
                    )
                    output.append(_hit)

    else:
        if verbose:
            print(
                LOCALIZE[get_region()]["warning_encoding_not_supported"],
                "\n * ",
                filename,
                file=sys.stderr,
            )

    return output, use_encoding


def paste_contents_into_file(other_file_names: list[str], target_file: TextIO):
    """
    Writes the contents of other files to the target file
    :param other_file_names: a list of path-likes pointing to source files
    :param target_file: path-like pointing to the destination file
    """

    target_file.write("\n")
    for file_name in other_file_names:
        with open(file_name, "r") as file:
            lines = file.readlines()

            for line in lines:
                line = f"{line}"
                target_file.write(line)

    target_file.write("\n")


def get_bot_submitted_issues(_test: bool = False) -> list[dict] or bool:
    """
    Makes a gh cli request for all issues submitted by app/todo-or-not, parses them, and returns them as a # todoon
    list of dicts
    :return: List of issues as dicts
    """
    owner, repo = "owner", "repository"

    try:
        if not (get_is_debug() or _test):
            owner, repo = os.environ.get("GITHUB_REPOSITORY").split("/")
    except AttributeError as e:
        print(
            f"{LOCALIZE[get_region()]['error_no_env']}: GITHUB_REPOSITORY", file=sys.stderr
        )

    query = [
        "gh",
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
        f"/repos/{owner}/{repo}/issues?creator=app%2Ftodo-or-not&state=all",  # todoon
    ]

    if not (get_is_debug() or _test):
        try:
            response = subprocess.check_output(query)
        except subprocess.CalledProcessError as e:
            print(e, file=sys.stderr)
            return False

        _str = response.decode("utf-8")
        _str.replace('"', '\\"')

        return json.loads(_str)
    else:
        print(query, file=sys.stderr)
        return False


def get_encoding(_target_path: str, _supported_encodings: list[str]) -> str or None:
    """
    :param _target_path: A path-like string pointing to the file for which we want to get a valid encoding
    :param _supported_encodings: A list of supported encodings e.g. `['utf-8', 'iso-8859-1', 'iso']`
    :return: The encoding of the target file if found, None if no supported encoding could be found
    """
    try:
        assert os.path.isfile(_target_path)
    except AssertionError:
        print(
            f"{LOCALIZE[get_region()]['error_is_not_file']}: {_target_path}", file=sys.stderr
        )
        return None

    # Try to read the file in a supported encoding
    _use_encoding = None
    for encoding in _supported_encodings:
        try:
            with open(_target_path, "r", encoding=encoding) as _ignore:
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


# fmt: off
@todoon_app.command(  # todoon
    help="Checks files for occurrences of TODO or FIXME and reports them for use with automation or other development operations.")  # todoon
def todoon(  # todoon
        files: Annotated[
            Optional[List[str]],
            typer.Argument(
                help="If specified, only these [FILES] will be scanned for TODOs and FIXMEs. "  # todoon
                     "Otherwise, all files in the current working directory except for those "
                     "specified in .todo-ignore will be scanned.")] = None,  # todoon
        print_mode: Annotated[
            bool,
            typer.Option("--print/--issue", "-p/-i",
                help="Whether to print the discovered TODOs and FIXMEs to stderr or to try"  # todoon
                     " an generate GitHub issues")] = True,
        silent: Annotated[
            bool,
            typer.Option("--silent/", "-s/",
                help="If specified, todoon will not exit with an error code even when TODOs and/or "  # todoon
                     "FIXMEs are detected")] = False,  # todoon
        fail_closed_duplicates: Annotated[
            bool,
            typer.Option("--closed-duplicates-fail/", "-c/",
                help="If specified, todoon will exit with error code if duplicate issues are found in a 'closed' state, will do so even if --silent/-s is specified")] = False,  # todoon
        force: Annotated[
            bool,
            typer.Option("--force/", "-f/",
                help="If specified, the .todo-ignore file will not be used. NOT RECOMMENDED")] = False,  # todoon
        verbose: Annotated[
            bool,
            typer.Option("--verbose/", "-v/",
                help="If specified, todoon will not to print lengthy or numerous messages"  # todoon
                     " (like each encoding failure)")] = False,
):
# fmt: on
    targets = []
    ignored_files = []
    ignored_dirs = []

    use_specified_files = False

    if files is not None and len(files) > 0:
        use_specified_files = True

    #############################################
    # Handle settings
    #############################################

    os.environ["TODOON_STATUS"] = "starting"  # todoon
    os.environ["TODOON_PROGRESS"] = "0.0"  # todoon
    os.environ["TODOON_FILES_SCANNED"] = "0"  # todoon
    os.environ["TODOON_TODOS_FOUND"] = "0"  # todoon
    os.environ["TODOON_FIXMES_FOUND"] = "0"  # todoon
    os.environ["TODOON_ENCODING_ERRORS"] = "0"  # todoon
    os.environ["TODOON_ISSUES_GENERATED"] = "0"  # todoon
    os.environ["TODOON_DUPLICATE_ISSUES_AVOIDED"] = "0"  # todoon

    #############################################
    # Parse .todo-ignore # todoon
    #############################################

    # If using specific files, no todo-ignore parsing is necessary # todoon
    if not use_specified_files:
        os.environ["TODOON_STATUS"] = "parsing-todo-ignore"  # todoon
        # As long as we aren't foregoing the .todo-ignore... # todoon
        if not force:
            # Unless --force is specified, a .todo-ignore in a supported encoding must be located at the project's top level # todoon
            use_encoding = get_encoding(
                get_todo_ignore_path(), SUPPORTED_ENCODINGS_TODOIGNORE  # todoon
            )

            # If we weren't able to find a file in a supported encoding, program must exit
            if use_encoding is None:
                print(
                    LOCALIZE[get_region()]["error_todo_ignore_not_supported"], file=sys.stderr  # todoon
                )
                exit(1)

            # ... actually do the reading of the .todo-ignore # todoon
            with open(
                    get_todo_ignore_path(), "r", encoding=use_encoding  # todoon
            ) as _ignore:
                for line in _ignore.readlines():
                    if not line.startswith("#") and len(line) > 1:
                        if line.endswith("\n"):
                            cur_name = line[:-1]
                        else:
                            cur_name = line

                        cur_path = os.path.join(get_project_dir(), cur_name)

                        # Resolve wildcards
                        if '*' in cur_path:
                            ignored_files.extend(glob.glob(cur_path, recursive=True))

                        if os.path.isfile(cur_path):
                            ignored_files.append(cur_path)

                        if os.path.isdir(cur_path):
                            ignored_dirs.append(cur_path)

                if len(ignored_files) == 0 and len(ignored_dirs) == 0:
                    print(
                        LOCALIZE[get_region()][
                            "warning_run_with_empty_todo_ignore"  # todoon
                        ],
                        file=sys.stderr,
                    )

                # Ignore the .todo-ignore itself # todoon
                ignored_files.append(os.path.abspath(_ignore.name))
        else:
            print(
                f"{LOCALIZE[get_region()]['error_todo_ignore_not_found']}"  # todoon
                f"[{LOCALIZE[get_os()]['shell_sigint']}]",
                file=sys.stderr,
            )

    #############################################
    # Collect files to scan
    #############################################

    # If using specific files, we will just parse them instead of walking
    if not use_specified_files:
        os.environ["TODOON_STATUS"] = "collecting-targets"  # todoon
        # Ignore this script if in DEBUG
        if get_is_debug():
            ignored_files.append(__file__)

        _walk = os.walk(get_project_dir(), topdown=True)

        for dirpath, dirnames, filenames in _walk:
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
    else:
        # Collect specified files
        for file in files:
            current_path = os.path.join(get_project_dir(), file)

            # If the specified path is a file, simply add it
            if os.path.isfile(current_path):
                targets.append(current_path)
                continue

            # If the specified path is a directory, add its children
            elif os.path.isdir(current_path):
                _walk = os.walk(current_path, topdown=True)

                for dirpath, dirnames, filenames in _walk:
                    for _filename in filenames:
                        filename = os.path.join(dirpath, _filename)
                        targets.append(filename)

    #############################################
    # Preventing duplicate issues
    #############################################

    # Warning if issues options are used when issue mode is not enabled
    if print_mode:
        if fail_closed_duplicates:
            print(
                f"{LOCALIZE[get_region()]['warning_nonissue_mode_closed_duplicate_used']}", file=sys.stderr
            )

    # When pinging for all queries their titles are hashed and saved here along with their state,
    # this is for checking for duplicate issues.
    # e.g. {"892f2a": "open", "39Ac9m": "closed"}
    existing_issues_hashed = {}

    # Collect all the issues that the bot has so far submitted to check for duplicates
    if not print_mode:

        os.environ["TODOON_STATUS"] = "collecting-issues"  # todoon
        todoon_created_issues = get_bot_submitted_issues()  # todoon

        if todoon_created_issues is not False:  # todoon
            for issue in todoon_created_issues:  # todoon
                existing_issues_hashed[_hash(issue["title"])] = issue["state"]
        else:
            print(
                f"{LOCALIZE[get_region()]['error_gh_issues_read_failed']}", file=sys.stderr
            )

    #############################################
    # Run todo-check # todoon
    #############################################

    number_of_hits = 0  # Tracks the number of targets found
    number_of_issues = 0  # Tracks the number of issues generated
    number_of_duplicate_issues_avoided = (
        0  # Tracks the number of issues avoided because they are already mentioned
    )
    number_of_closed_issues = 0
    number_of_encoding_failures = 0  # Tracks the files unread due to encoding error
    number_of_files_scanned = len(
        targets
    )  # Tracks the files attempted to be read, regardless of errors

    # Used for summary
    number_of_todo, number_of_fixme = 0, 0  # todoon

    os.environ["TODOON_STATUS"] = "scanning-files"  # todoon
    os.environ["TODOON_PROGRESS"] = "0.0"  # todoon
    # For each target file discovered
    _i = 0
    for target in targets:

        # Update progress
        _i += 1
        os.environ["TODOON_PROGRESS"] = str(round(_i / (len(targets)), 1))  # todoon

        # Generate the hits for each target collected
        hits, _enc = find_lines(target, verbose, "# todoon", "todo", "fixme")

        if _enc is None:
            number_of_encoding_failures += 1

        # If any hits were detected...
        if len(hits) > 0:

            # Handle each hit that was detected
            for hit in hits:
                number_of_hits += 1
                number_of_todo += 1 if "todo" in hit.found_keys else 0  # todoon
                number_of_fixme += 1 if "fixme" in hit.found_keys else 0  # todoon

                #############################################
                # Special handling for the ISSUE mode

                if not print_mode:
                    _this_hit_hashed = _hash(hit.get_title())

                    # Check if the app already created this hit's title in open AND closed issues
                    if _this_hit_hashed not in existing_issues_hashed:

                        # Limit the number of issues created in one run
                        if number_of_issues < get_max_issues():
                            output = hit.generate_issue()

                            if output is not False:
                                number_of_issues += 1
                            else:
                                print(
                                    f"{LOCALIZE[get_region()]['error_gh_issues_create_failed']}", file=sys.stderr
                                )

                        else:
                            print(
                                LOCALIZE[get_region()][
                                    "error_exceeded_maximum_issues"
                                ],
                                file=sys.stderr,
                            )
                            exit(1)
                    # If this title exists AND is closed, potentially fail the check
                    elif existing_issues_hashed[_this_hit_hashed] == "closed":
                        print(
                            f"{LOCALIZE[get_region()]['warning_duplicate_closed_issue']}: {hit}", file=sys.stderr
                        )
                        number_of_closed_issues += 1
                    # If this title already exists, notify but do not halt
                    else:
                        print(
                            f"{LOCALIZE[get_region()]['info_duplicate_issue_avoided']}: {hit}",
                            file=sys.stderr,
                        )
                        number_of_duplicate_issues_avoided += 1

                #############################################
                # If not in ISSUE mode, print hit to stderr

                else:
                    print(hit, file=sys.stderr)

    #############################################
    # Summarize the run of todo-check  # todoon
    #############################################

    summary = f"\n##########################\n# {LOCALIZE[get_region()]['summary_title']}\n"
    # Mode the tool was run in
    if print_mode:
        summary += "# (PRINT MODE)\n"
    else:
        summary += "# (ISSUE MODE)\n"

    # Number of TODOs and FIXMEs found  # todoon
    summary += f"# {number_of_todo} TODO | {number_of_fixme} FIXME\n"  # todoon

    # Number of encoding failures
    if number_of_encoding_failures > 1:
        summary += f"# {number_of_encoding_failures} {LOCALIZE[get_region()]['summary_encoding_unsupported_plural']}\n"
    elif number_of_encoding_failures == 1:
        summary += f"# {number_of_encoding_failures} {LOCALIZE[get_region()]['summary_encoding_unsupported_singular']}\n"

    # Total number of files scanned
    if number_of_files_scanned > 1:
        summary += (f"# {number_of_files_scanned} "
                    f"{LOCALIZE[get_region()]['summary_files_scanned_plural']}\n")
    elif number_of_files_scanned == 1:
        summary += (f"# {number_of_files_scanned} "
                    f"{LOCALIZE[get_region()]['summary_files_scanned_singular']}\n")

        # Number of issues (if any) that were generated
    if not print_mode:
        # Total number of issues generated
        if number_of_issues > 1:
            summary += (f"# {number_of_issues} "
                        f"{LOCALIZE[get_region()]['summary_issues_generated_plural']}\n")
        elif number_of_issues == 1:
            summary += (f"# {number_of_issues} "
                        f"{LOCALIZE[get_region()]['summary_issues_generated_singular']}\n")
        else:
            summary += (f"# "
                        f"{LOCALIZE[get_region()]['summary_issues_generated_none']}\n")

        # Total number of duplicate issues avoided
        if number_of_duplicate_issues_avoided > 1:
            summary += (f"# {number_of_duplicate_issues_avoided} "
                        f"{LOCALIZE[get_region()]['summary_duplicate_issues_avoided_plural']}\n")
        elif number_of_duplicate_issues_avoided == 1:
            summary += (f"# {number_of_duplicate_issues_avoided} "
                        f"{LOCALIZE[get_region()]['summary_duplicate_issues_avoided_singular']}\n")

        # Total number of duplicate closed issues
        if number_of_closed_issues > 1:
            summary += (f"# {number_of_closed_issues} "
                        f"{LOCALIZE[get_region()]['summary_duplicate_closed_issues_plural']}\n")
        elif number_of_closed_issues == 1:
            summary += (f"# {number_of_closed_issues} "
                        f"{LOCALIZE[get_region()]['summary_duplicate_closed_issues_singular']}\n")

    summary += "##########################\n\n"

    # Fail reasons
    if number_of_hits > 0 and not silent:
        summary += (f"  * {LOCALIZE[get_region()]['summary_fail_issues_no_silent']}\n")

    if number_of_closed_issues > 0 and fail_closed_duplicates:
        summary += (f"  * {LOCALIZE[get_region()]['summary_fail_duplicate_closed_issues']}\n")


    os.environ["TODOON_STATUS"] = "finished"  # todoon
    os.environ["TODOON_PROGRESS"] = "100.0"  # todoon
    os.environ["TODOON_FILES_SCANNED"] = str(number_of_files_scanned)  # todoon
    os.environ["TODOON_TODOS_FOUND"] = str(number_of_todo)  # todoon
    os.environ["TODOON_FIXMES_FOUND"] = str(number_of_fixme)  # todoon
    os.environ["TODOON_ENCODING_ERRORS"] = str(number_of_encoding_failures)  # todoon
    os.environ["TODOON_ISSUES_GENERATED"] = str(number_of_issues)  # todoon
    os.environ["TODOON_DUPLICATE_ISSUES_AVOIDED"] = str(  # todoon
        number_of_duplicate_issues_avoided
    )
    os.environ["TODOON_DUPLICATE_CLOSED_ISSUES"] = str(  # todoon
        number_of_closed_issues
    )

    print(summary, file=sys.stderr)

    # Fail if any hits were found and we are not in silent mode
    if number_of_hits > 0 and not silent:
        exit(1)

    # Fail if any closed duplicates were found and we are set to fail if so
    if number_of_closed_issues > 0 and fail_closed_duplicates:
        exit(1)

# fmt: off
@todoon_app.command(help="Small utility for generating a .todo-ignore file")  # todoon
def todo_ignore_util(  # todoon
        sources: Annotated[
            Optional[List[str]],
            typer.Argument(
                help="(default) [with -p] Files whose contents will be added to the .todo-ignore file.\n\n          "  # todoon
                     "[with -t] Lines of text to be added to the .todo-ignore file.")] = None,  # todoon
        create_mode: Annotated[
            bool,
            typer.Option("--create/--update", "-c/-u",
                help="Whether to create a new .todo-ignore file or update an existing one")] = True,  # todoon
        source_is_text: Annotated[bool, typer.Option("--source-text/--source-paths", "-t/-p",
                                                     help="Whether to treat SOURCES as text or as file paths.")] = True
):
#fmt: on
    todoignore_path = os.path.join(os.getcwd(), ".todo-ignore")  # todoon
    output = []

    if create_mode:
        access_mode = "x"
    else:
        access_mode = "a"

    if source_is_text:
        if sources is not None and len(sources) > 0:
            output.extend(sources)
    else:
        if sources is not None and len(sources) > 0:
            for file in sources:
                _path = os.path.join(os.getcwd(), file)

                try:
                    with (open(_path, "r")) as current:
                        _current_lines = current.readlines()

                        for line in _current_lines:
                            line = line.strip()

                            if len(line) > 0:
                                output.append(line)
                except FileNotFoundError:
                    print(LOCALIZE[get_region()]["warning_file_does_not_exist"], _path, file=sys.stderr)

    try:
        with open(todoignore_path, access_mode) as target:  # todoon
            previous = None
            for line in output:
                if previous != line[0]:
                    target.write('\n')
                previous = line[0]

                target.write(f"{line}\n")
    except FileExistsError:
        print(
            LOCALIZE[get_region()]["error_file_already_exists"], todoignore_path, file=sys.stderr  # todoon
        )
        exit(1)

    print(LOCALIZE[get_region()]["general_done"])


def typer_todoon():  # todoon
    run(todoon)  # todoon


def typer_todo_ignore_util():  # todoon
    run(todo_ignore_util)  # todoon


if __name__ == "__main__":
    todoon_app()  # todoon
