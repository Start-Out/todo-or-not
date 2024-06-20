import os
import subprocess
import sys

import todo_or_not.utility as util


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

        location = os.path.relpath(self.source_file, os.getcwd())
        location = f"{location}:{_line_number}"
        _pad = 16 - len(location)
        padding = " " * _pad
        location = location + padding

        return f"{header} - {location} - {_line.strip()}"

    def __eq__(self, other):
        if not isinstance(other, Hit):
            # don't attempt to compare against unrelated types
            return NotImplemented

        if self.structured_labels is not None and other.structured_labels is not None:
            return set(self.structured_labels) == set(other.structured_labels)

        # Forgive this monstrosity, it helps find what is different during debugging sessions.
        a = True
        a = False if not set(self.found_keys) == set(other.found_keys) else a
        a = False if not self.source_file == other.source_file else a
        a = False if not self.source_line == other.source_line else a
        a = False if not set(self.pertinent_lines) == set(other.pertinent_lines) else a
        a = False if not self.trigger_line_index == other.trigger_line_index else a
        a = False if not self.structured_title == other.structured_title else a
        a = False if not self.structured_body == other.structured_body else a

        return a

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

    def generate_issue(
        self, _test: bool = False, log_level=util.LOG_LEVEL_NORMAL
    ) -> str or bool:

        repo_uri = f"https://github.com/None"

        github_ref = "$NONE"
        triggered_by = "$NONE"
        owner, repo = "$NONE", "$NONE"

        if not (util.get_is_debug() or _test):
            repo_uri = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}"

            github_ref = os.environ.get("GITHUB_REF_NAME", "$NONE")
            triggered_by = os.environ.get("GITHUB_TRIGGERING_ACTOR", "$NONE")
            owner, repo = os.environ.get("GITHUB_REPOSITORY", "$NONE/$NONE").split("/")

            # Find missing env variables
            missing_envs = []

            if github_ref == "$NONE":
                util.print_wrap(
                    log_level=log_level,
                    msg=f"{util.LOCALIZE[util.get_region()]['error_no_env']}: GITHUB_REF_NAME",
                    file=sys.stderr,
                )
                missing_envs.append("GITHUB_REF_NAME")
            if triggered_by == "$NONE":
                util.print_wrap(
                    log_level=log_level,
                    msg=f"{util.LOCALIZE[util.get_region()]['error_no_env']}: GITHUB_TRIGGERING_ACTOR",
                    file=sys.stderr,
                )
                missing_envs.append("GITHUB_TRIGGERING_ACTOR")
            if owner == "$NONE":
                util.print_wrap(
                    log_level=log_level,
                    msg=f"{util.LOCALIZE[util.get_region()]['error_no_env']}: GITHUB_REPOSITORY",
                    file=sys.stderr,
                )
                missing_envs.append("GITHUB_REPOSITORY")
            if repo == "$NONE":
                util.print_wrap(
                    log_level=log_level,
                    msg=f"{util.LOCALIZE[util.get_region()]['error_no_env']}: GITHUB_REPOSITORY",
                    file=sys.stderr,
                )
                missing_envs.append("GITHUB_REPOSITORY")

            if len(missing_envs) > 0:
                return False

        reference_file = self.source_file.split(":")[0]

        reference_uri = f"{repo_uri}/blob/{github_ref}/{reference_file}"

        body = (
            f"## {self if self.structured_body is None else self.structured_body}\n\n"
            f"{self.get_pertinent_lines()}\n\n"
            f"{util.LOCALIZE[util.get_region()]['issue_body_reference_link']}: <a href=\"{reference_uri}\">{self.source_file}</a>"
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

        if not (util.get_is_debug() or _test):
            try:
                _output = subprocess.check_output(api_call)
            except subprocess.CalledProcessError as e:
                util.print_wrap(log_level=log_level, msg=str(e), file=sys.stderr)
                _output = False
        else:
            _output = True
            util.print_wrap(log_level=log_level, msg=str(api_call))

        return _output
