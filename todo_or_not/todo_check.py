import glob
import json
import os
import subprocess
import sys
from typing import List, Optional, TextIO

import typer
from tqdm import tqdm
from typer import run
from typing_extensions import Annotated

import todo_or_not.utility as util
from todo_or_not.utility import loc
from todo_or_not.todo_app import TodoRun
from todo_or_not.localize import LOCALIZE
from todo_or_not.localize import SUPPORTED_ENCODINGS_TODOIGNORE
from todo_or_not.localize import SUPPORTED_ENCODINGS_TODO_CHECK
from todo_or_not.todo_grammar import find_language, TodoGrammar
from todo_or_not.todo_hit import Hit

todoon_app = typer.Typer(name="todoon")


def find_hits(
    filename: str, ignore_flag: str, parsers: dict, log_level=util.LOG_LEVEL_NORMAL
) -> tuple[list[Hit], str or None]:
    """
    Finds and returns each line of a file that contains a key
    :param ignore_flag: The flag which, when detected on a triggering line, will ignore that line
    :param filename: File to open() read-only
    :param parsers: Parsers that have been built for discovered languages
    :param log_level: The importance of any feedback prints (e.g. 0=NONE, 3=VERBOSE)
    :return:
     | List of lines of text and their line number that contain at least one key and the keys each contains
     | The detected encoding of the file or none if not found
    """
    output = []

    use_encoding = get_encoding(filename, SUPPORTED_ENCODINGS_TODO_CHECK)

    if use_encoding is not None:
        with open(filename, "r", encoding=use_encoding) as file:
            # Get the extension of this file and parse its language, note that several extensions may be associated
            # with a single language, so we must find the language common to those extensions.
            file_extension = filename.rsplit(".", 1)[-1]
            file_language = find_language(file_extension)

            # If that language does not yet have a parser built, we must build one (note that calling the
            # TodoGrammar constructor with the file_extension will functional identically between different  # todoon
            # file extensions for the same language)
            if file_language not in parsers.keys():
                parsers[file_language] = TodoGrammar(file_extension)
                parsers[file_language].build()

            line_number = 0
            lines = file.readlines()

            for _line in lines:
                line_number += 1

                # Ignore this line if the ignore flag is present
                if ignore_flag in _line:
                    continue

                _use_parser = parsers[file_language]
                _potential_hit = _use_parser.safe_parse(_line)

                if _potential_hit:
                    # Collect surrounding lines that may be pertinent
                    _pertinent_lines = []

                    # Look at lines before the pertinent line
                    _i = line_number - 1
                    while (
                        abs(line_number - _i) <= util.get_pertinent_line_limit()
                        and _i >= 0
                    ):
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
                    while abs(_i - line_number) <= util.get_pertinent_line_limit():
                        if _i < len(lines) and len(lines[_i].strip()) > 0:
                            _pertinent_lines.append(lines[_i])
                        else:
                            # Stop when you reach a line break
                            break
                        _i += 1

                    _potential_hit.source_file = os.path.relpath(filename, os.getcwd())
                    _potential_hit.source_line = line_number
                    _potential_hit.pertinent_lines = _pertinent_lines
                    _potential_hit.trigger_line_index = _trigger_line

                    output.append(_potential_hit)

    else:
        util.print_wrap(
            log_level=log_level,
            msg_level=util.LOG_LEVEL_VERBOSE,
            msg=f"{loc('warning_encoding_not_supported')} \n * {filename}",
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


def get_bot_submitted_issues(
    _test: bool = False, log_level=util.LOG_LEVEL_NORMAL
) -> list[dict] or bool:
    """
    Makes a gh cli request for all issues submitted by app/todo-or-not, parses them, and returns them as a # todoon
    list of dicts
    :return: List of issues as dicts
    """
    owner, repo = "owner", "repository"

    try:
        if not (util.get_is_debug() or _test):
            owner, repo = os.environ.get("GITHUB_REPOSITORY").split("/")
    except AttributeError as _:
        util.print_wrap(
            log_level=log_level,
            msg=f"{loc('error_no_env')}: GITHUB_REPOSITORY",
            file=sys.stderr,
        )

    query = [
        "gh",
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
        f"/repos/{owner}/{repo}/issues?creator=app%2Ftodo-or-not&state=all",
    ]

    if not (util.get_is_debug() or _test):
        try:
            response = subprocess.check_output(query)
        except subprocess.CalledProcessError as e:
            util.print_wrap(log_level=log_level, msg=str(e), file=sys.stderr)
            return False

        _str = response.decode("utf-8")
        _str.replace('"', '\\"')

        return json.loads(_str)
    else:
        util.print_wrap(log_level=log_level, msg=str(query), file=sys.stderr)
        return False


def get_encoding(
    _target_path: str, _supported_encodings: list[str], log_level=util.LOG_LEVEL_NORMAL
) -> str or None:
    """
    :param _target_path: A path-like string pointing to the file for which we want to get a valid encoding
    :param _supported_encodings: A list of supported encodings e.g. `['utf-8', 'iso-8859-1', 'iso']`
    :param log_level: The importance of any feedback prints (e.g. 0=NONE, 3=VERBOSE)
    :return: The encoding of the target file if found, None if no supported encoding could be found
    """
    try:
        assert os.path.isfile(_target_path)
    except AssertionError:
        util.print_wrap(
            log_level=log_level,
            msg=f"{loc('error_is_not_file')}: {_target_path}",
            file=sys.stderr,
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
@todoon_app.command(
    help="Checks files for occurrences of TODO or FIXME and reports them for use with automation or "
         "other development operations")
def todoon(
        files: Annotated[
            Optional[List[str]],
            typer.Argument(
                help="If specified, only these [FILES] will be scanned for TODOs and FIXMEs. "
                     "Otherwise, all files in the current working directory except for those "
                     "specified in .todo-ignore will be scanned")] = None,
        print_mode: Annotated[
            bool,
            typer.Option("--print/--issue", "-p/-i",
                         help="Whether to print the discovered TODOs and FIXMEs to stderr or to try"
                              " generating GitHub issues")] = True,
        silent: Annotated[
            bool,
            typer.Option("--silent/", "-s/",
                         help="(No fail) If specified, todoon will not exit with an error code even "
                              "when TODOs and/or FIXMEs are detected")] = False,
        fail_closed_duplicates: Annotated[
            bool,
            typer.Option("--closed-duplicates-fail/", "-c/",
                         help="If specified, todoon will exit with error code if duplicate GitHub issues "
                              "are found in a 'closed' state, will do so even if --silent/-s is specified")] = False,
        push_github_env_vars: Annotated[
            bool,
            typer.Option("--github-env/",
                         help="If specified, todoon will push environment variables to the special $GITHUB_ENV "
                              "file. This allows the variables to persist across steps in a workflow.")] = False,
        force: Annotated[
            bool,
            typer.Option("--force/", "-f/",
                         help="(NOT RECOMMENDED) If specified, no .todo-ignore file will be used")] = False,
        verbose: Annotated[
            bool,
            typer.Option("--verbose/", "-V/",
                         help="If specified, todoon will not to print lengthy or numerous messages "
                              "(like each encoding failure)")] = False,
        print_summary_only: Annotated[
            bool,
            typer.Option("--quiet/", "-q/",
                         help="If specified, todoon will only print the summary")] = False,
        print_nothing: Annotated[
            bool,
            typer.Option("--very-quiet/", "-Q/",
                         help="If specified, todoon will not print anything at all")] = False,
        show_progress_bar: Annotated[
            bool,
            typer.Option("--progress-bar/", "-P/",
                         help="If specified, todoon will display a progress bar while scanning files. "
                              "NOTE: This adds a small amount of overhead (will take a little longer)")] = False,
        version: Annotated[
            bool,
            typer.Option("--version/", "-v/",
                         help="Show the application version and exit.")] = False
):
    # fmt: on
    this_run = TodoRun({
        "files": files,
        "print_mode": print_mode,
        "silent": silent,
        "fail_closed_duplicates": fail_closed_duplicates,
        "push_github_env_vars": push_github_env_vars,
        "force": force,
        "verbose": verbose,
        "print_summary_only": print_summary_only,
        "print_nothing": print_nothing,
        "show_progress_bar": show_progress_bar,
        "version": version
    })

    targets = []
    ignored_files = []
    ignored_dirs = []

    log_level = util.LOG_LEVEL_NORMAL
    if verbose:
        log_level = util.LOG_LEVEL_VERBOSE
    if print_summary_only:
        log_level = util.LOG_LEVEL_SUMMARY_ONLY
    if print_nothing:
        log_level = util.LOG_LEVEL_NONE

    use_specified_files = False

    if files is not None and len(files) > 0:
        use_specified_files = True

    if version:
        util.version_callback()

    #############################################
    # Handle settings
    #############################################

    this_run.initialize_environment_variables()

    #############################################
    # Parse .todo-ignore # todoon
    #############################################

    # If using specific files, no todo-ignore parsing is necessary # todoon
    if not use_specified_files:
        os.environ["TODOON_STATUS"] = "parsing-todo-ignore"
        # As long as we aren't foregoing the .todo-ignore... # todoon
        if not force:
            # Unless --force is specified,
            # a .todo-ignore in a supported encoding must be located at the project's top level # todoon
            use_encoding = get_encoding(
                util.get_todo_ignore_path(), SUPPORTED_ENCODINGS_TODOIGNORE
            )

            # If we weren't able to find a file in a supported encoding, program must exit
            if use_encoding is None:
                util.print_wrap(log_level=log_level,
                                msg=loc("error_todo_ignore_not_supported"),
                                file=sys.stderr
                                )
                sys.exit(1)

            # ... actually do the reading of the .todo-ignore # todoon
            with open(
                    util.get_todo_ignore_path(), "r", encoding=use_encoding
            ) as _ignore:
                for line in _ignore.readlines():
                    if not line.startswith("#") and len(line) > 1:
                        if line.endswith("\n"):
                            cur_name = line[:-1]
                        else:
                            cur_name = line

                        cur_path = os.path.join(os.getcwd(), cur_name)

                        # Resolve wildcards
                        if '*' in cur_path:
                            ignored_files.extend(glob.glob(cur_path, recursive=True))

                        if os.path.isfile(cur_path):
                            ignored_files.append(cur_path)

                        if os.path.isdir(cur_path):
                            ignored_dirs.append(cur_path)

                if len(ignored_files) == 0 and len(ignored_dirs) == 0:
                    util.print_wrap(log_level=log_level,
                                    msg=loc("warning_run_with_empty_todo_ignore"),
                                    file=sys.stderr,
                                    )

                # Ignore the .todo-ignore itself # todoon
                ignored_files.append(os.path.abspath(_ignore.name))
        else:
            util.print_wrap(log_level=log_level,
                            msg=f"{loc('error_todo_ignore_not_found')}"
                                f"[{LOCALIZE[util.get_os()]['shell_sigint']}]",
                            file=sys.stderr,
                            )

    #############################################
    # Collect files to scan
    #############################################

    # If using specific files, we will just parse them instead of walking
    if not use_specified_files:
        os.environ["TODOON_STATUS"] = "collecting-targets"
        # Ignore this script if in DEBUG
        if util.get_is_debug():
            ignored_files.append(__file__)

        _walk = os.walk(os.getcwd(), topdown=True)

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
            current_path = os.path.join(os.getcwd(), file)

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
            util.print_wrap(log_level=log_level,
                            msg=f"{loc('warning_nonissue_mode_closed_duplicate_used')}",
                            file=sys.stderr
                            )

    # When pinging for all queries their titles are hashed and saved here along with their state,
    # this is for checking for duplicate issues.
    # e.g. {"892f2a": "open", "39Ac9m": "closed"}
    existing_issues_hashed = {}

    # Collect all the issues that the bot has so far submitted to check for duplicates
    if not print_mode:

        os.environ["TODOON_STATUS"] = "collecting-issues"
        todoon_created_issues = get_bot_submitted_issues()

        if todoon_created_issues is not False:
            for issue in todoon_created_issues:
                existing_issues_hashed[util.sha1_hash(issue["title"])] = issue["state"]
        else:
            util.print_wrap(log_level=log_level,
                            msg=f"{loc('error_gh_issues_read_failed')}", file=sys.stderr
                            )

    #############################################
    # Run todo-check # todoon
    #############################################

    # Tracks the files attempted to be read, regardless of errors
    this_run.number_of_files_scanned = len(
        targets
    )

    os.environ["TODOON_STATUS"] = "scanning-files"
    os.environ["TODOON_PROGRESS"] = "0.0"
    # For each target file discovered
    _i = 0
    _target_iterator = targets

    if show_progress_bar:
        _target_iterator = tqdm(targets, unit=loc('progress_bar_run_unit'),
                                desc=loc('progress_bar_run_desc'))

    for target in _target_iterator:

        # Update progress
        _i += 1
        os.environ["TODOON_PROGRESS"] = str(round(_i / (len(targets)), 1))

        parsers = {}

        # Generate the hits for each target collected
        hits, _enc = find_hits(target, "# todoon", parsers, log_level=log_level)

        if _enc is None:
            this_run.number_of_encoding_failures += 1

        # If any hits were detected...
        if len(hits) > 0:

            # Handle each hit that was detected
            for hit in hits:
                this_run.number_of_hits += 1
                this_run.number_of_todo += 1 if "todo" in hit.found_keys else 0
                this_run.number_of_fixme += 1 if "fixme" in hit.found_keys else 0

                #############################################
                # Special handling for the ISSUE mode

                if not print_mode:
                    _this_hit_hashed = util.sha1_hash(hit.get_title())

                    # Check if the app already created this hit's title in open AND closed issues
                    if _this_hit_hashed not in existing_issues_hashed:

                        # Limit the number of issues created in one run
                        if this_run.number_of_issues < util.get_max_issues():
                            output = hit.generate_issue()

                            if output is not False:
                                this_run.number_of_issues += 1
                            else:
                                util.print_wrap(log_level=log_level,
                                                msg=f"{loc('error_gh_issues_create_failed')}",
                                                file=sys.stderr
                                                )

                        else:
                            util.print_wrap(log_level=log_level,
                                            msg=loc("error_exceeded_maximum_issues"),
                                            file=sys.stderr,
                                            )
                            sys.exit(1)
                    # If this title exists AND is closed, potentially fail the check
                    elif existing_issues_hashed[_this_hit_hashed] == "closed":
                        util.print_wrap(log_level=log_level,
                                        msg=f"{loc('warning_duplicate_closed_issue')}: {hit}",
                                        file=sys.stderr
                                        )
                        this_run.number_of_closed_issues += 1
                    # If this title already exists, notify but do not halt
                    else:
                        util.print_wrap(log_level=log_level,
                                        msg=f"{loc('info_duplicate_issue_avoided')}: {hit}",
                                        file=sys.stderr,
                                        )
                        this_run.number_of_duplicate_issues_avoided += 1

                #############################################
                # If not in ISSUE mode, print hit to stderr

                else:
                    util.print_wrap(log_level=log_level,
                                    msg=str(hit), file=sys.stderr)

    #############################################
    # Summarize the run of todo-check  # todoon
    #############################################

    summary = this_run.generate_summary_message()

    this_run.report_environment_variables()

    util.print_wrap(log_level=log_level, msg_level=util.LOG_LEVEL_SUMMARY_ONLY,
                    msg=summary, file=sys.stderr)

    # Fail if any hits were found and we are not in silent mode
    if this_run.number_of_hits > 0 and not silent:
        sys.exit(1)

    # Fail if any closed duplicates were found and we are set to fail if so
    if this_run.number_of_closed_issues > 0 and fail_closed_duplicates:
        sys.exit(1)


# fmt: off
@todoon_app.command(help="Small utility for generating a .todo-ignore file")
def todo_ignore_util(
        sources: Annotated[
            Optional[List[str]],
            typer.Argument(
                help="(default) [with -p] Files whose contents will be added to the "
                     ".todo-ignore file.\n\n          "
                     "[with -t] Lines of text to be added to the .todo-ignore file.")] = None,
        create_mode: Annotated[
            bool,
            typer.Option("--create/--update", "-c/-u",
                         help="Whether to create a new .todo-ignore file or update an existing one")] = True,
        source_is_text: Annotated[bool, typer.Option("--source-text/--source-paths", "-t/-p",
                                                     help="Whether to treat SOURCES as text or as file paths.")] = True
):
    # fmt: on
    todoignore_path = os.path.join(os.getcwd(), ".todo-ignore")
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
                    print(loc("warning_file_does_not_exist"), _path, file=sys.stderr)
                except IsADirectoryError:
                    print(loc("warning_is_a_directory"), _path, file=sys.stderr)

    try:
        with open(todoignore_path, access_mode) as target:
            previous = None
            for line in output:
                if previous != line[0]:
                    target.write('\n')
                previous = line[0]

                target.write(f"{line}\n")
    except FileExistsError:
        print(
            loc("error_file_already_exists"), todoignore_path, file=sys.stderr
        )
        sys.exit(1)

    print(loc("general_done"))


def typer_todoon():
    run(todoon)


def typer_todo_ignore_util():
    run(todo_ignore_util)


if __name__ == "__main__":
    todoon_app()
