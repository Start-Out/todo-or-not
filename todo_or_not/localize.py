SUPPORTED_ENCODINGS_TODOIGNORE = ['utf-8', 'utf-16']
SUPPORTED_ENCODINGS_TODO_CHECK = ['utf-8']

LOCALIZE = {
    "en_us": {
        "reference_link": "Reference",
        "summary": "Summary",
        "info_duplicate_issue_avoided": "INFO: Duplicate issue avoided",
        "error_cannot_specify_ni_xi": "ERROR: Cannot specify both --ni and --xi",
        "error_todo_ignore_not_found": "ERROR: .todo-ignore NOT FOUND! use -i to copy another .ignore OR --force to run without a .todo-ignore (NOT RECOMMENDED)",
        "error_todo_ignore_not_supported": f"ERROR: .todo-ignore uses unsupported encoding! Supported encodings: {SUPPORTED_ENCODINGS_TODOIGNORE}",
        "error_exceeded_maximum_issues": "ERROR: Exceeded maximum number of issues for this run, exiting now",
        "warning_force_overrides_ignore": "WARNING: --force will ignore the contents of the .todo-ignore generated when you specified (.todo-ignore will still be changed, just not used)",
        "warning_run_without_todo_ignore": "WARNING: Running without a .todo-ignore, to cancel use "
    },
    "windows": {
        "shell_sigint": "CTRL + C"
    }
}
