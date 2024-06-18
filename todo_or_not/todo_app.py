import os

from todo_or_not.utility import loc

class TodoRun:
    def __init__(self, settings: dict):
        self.fail_closed_duplicates = settings["fail_closed_duplicates"]
        self.silent = settings["silent"]
        self.print_mode = settings["print_mode"]

        # Tracks the files attempted to be read, regardless of errors
        self.number_of_files_scanned = 0

        # Tracks the files unread due to encoding error
        self.number_of_encoding_failures = 0

        # Tracks the number of targets found
        self.number_of_hits = 0
        self.number_of_todo = 0
        self.number_of_fixme = 0

        # Tracks the number of issues generated
        self.number_of_issues = 0

        # Tracks the number of issues avoided because they are already mentioned
        self.number_of_duplicate_issues_avoided = 0

        # Tracks the number of issues found that may already be "Closed" on GitHub
        self.number_of_closed_issues = 0

    @staticmethod
    def initialize_environment_variables():
        os.environ["TODOON_STATUS"] = "starting"
        os.environ["TODOON_PROGRESS"] = "0.0"
        os.environ["TODOON_FILES_SCANNED"] = "0"
        os.environ["TODOON_TODOS_FOUND"] = "0"
        os.environ["TODOON_FIXMES_FOUND"] = "0"
        os.environ["TODOON_ENCODING_ERRORS"] = "0"
        os.environ["TODOON_ISSUES_GENERATED"] = "0"
        os.environ["TODOON_DUPLICATE_ISSUES_AVOIDED"] = "0"

    def generate_summary_message(self):
        summary = f"\n##########################\n# {loc('summary_title')}\n"
        # Mode the tool was run in
        if self.print_mode:
            summary += "# (PRINT MODE)\n"
        else:
            summary += "# (ISSUE MODE)\n"

        # Number of TODOs and FIXMEs found  # todoon
        summary += f"# {self.number_of_todo} TODO | {self.number_of_fixme} FIXME\n"  # todoon

        # Number of encoding failures
        if self.number_of_encoding_failures > 1:
            summary += f"# {self.number_of_encoding_failures} {loc('summary_encoding_unsupported_plural')}\n"
        elif self.number_of_encoding_failures == 1:
            summary += f"# {self.number_of_encoding_failures} {loc('summary_encoding_unsupported_singular')}\n"

        # Total number of files scanned
        if self.number_of_files_scanned > 1:
            summary += (f"# {self.number_of_files_scanned} "
                        f"{loc('summary_files_scanned_plural')}\n")
        elif self.number_of_files_scanned == 1:
            summary += (f"# {self.number_of_files_scanned} "
                        f"{loc('summary_files_scanned_singular')}\n")

            # Number of issues (if any) that were generated
        if not self.print_mode:
            # Total number of issues generated
            if self.number_of_issues > 1:
                summary += (f"# {self.number_of_issues} "
                            f"{loc('summary_issues_generated_plural')}\n")
            elif self.number_of_issues == 1:
                summary += (f"# {self.number_of_issues} "
                            f"{loc('summary_issues_generated_singular')}\n")
            else:
                summary += (f"# "
                            f"{loc('summary_issues_generated_none')}\n")

            # Total number of duplicate issues avoided
            if self.number_of_duplicate_issues_avoided > 1:
                summary += (f"# {self.number_of_duplicate_issues_avoided} "
                            f"{loc('summary_duplicate_issues_avoided_plural')}\n")
            elif self.number_of_duplicate_issues_avoided == 1:
                summary += (f"# {self.number_of_duplicate_issues_avoided} "
                            f"{loc('summary_duplicate_issues_avoided_singular')}\n")

            # Total number of duplicate closed issues
            if self.number_of_closed_issues > 1:
                summary += (f"# {self.number_of_closed_issues} "
                            f"{loc('summary_duplicate_closed_issues_plural')}\n")
            elif self.number_of_closed_issues == 1:
                summary += (f"# {self.number_of_closed_issues} "
                            f"{loc('summary_duplicate_closed_issues_singular')}\n")

        summary += "##########################\n\n"

        # Overall results of the run
        if self.number_of_hits > 0:
            if self.silent:
                summary += f"  * {loc('summary_found_issues_silent')}\n"
            else:
                summary += f"  * {loc('summary_fail_issues_no_silent')}\n"

        if self.number_of_closed_issues > 0 and self.fail_closed_duplicates:
            summary += f"  * {loc('summary_fail_duplicate_closed_issues')}\n"

        # Total success
        if self.number_of_hits == 0:
            summary += f"  * {loc('summary_success')}\n"

        return summary
