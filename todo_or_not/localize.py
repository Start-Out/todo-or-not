SUPPORTED_ENCODINGS_TODOIGNORE = ['utf-8', 'utf-16']
SUPPORTED_ENCODINGS_TODO_CHECK = ['utf-8', 'utf-16']

LOCALIZE = {
    "en_us": {
        "issue_body_reference_link": "Reference",
        "summary_title": "Summary",
        "summary_encoding_unsupported_singular": "File skipped due to unsupported encoding",
        "summary_encoding_unsupported_plural": "Files skipped due to unsupported encodings",
        "info_duplicate_issue_avoided": "INFO: Duplicate issue avoided",
        "error_cannot_specify_ni_xi": "ERROR: Cannot specify both --ni and --xi",
        "error_is_not_file": "ERROR: Specified path is not a file",
        "error_todo_ignore_not_found": "ERROR: .todo-ignore NOT FOUND! use -i to copy another .ignore OR --force to run without a .todo-ignore (NOT RECOMMENDED)",
        "error_todo_ignore_not_supported": f"ERROR: .todo-ignore uses unsupported encoding or doesn't exist! Supported encodings: {SUPPORTED_ENCODINGS_TODOIGNORE}",
        "error_exceeded_maximum_issues": "ERROR: Exceeded maximum number of issues for this run, exiting now",
        "warning_force_overrides_ignore": "WARNING: --force will ignore the contents of the .todo-ignore generated when you specified (.todo-ignore will still be changed, just not used)",
        "warning_run_with_empty_todo_ignore": "WARNING: .todo-ignore was empty (if the file isn't empty, check its encoding), running anyway. To cancel use ",
        "warning_run_without_todo_ignore": "WARNING: Running without a .todo-ignore, to cancel use ",
        "warning_encoding_not_supported": f"WARNING: File uses unsupported encoding, we will skip it but consider adding to .todo-ignore (Supported encodings: {SUPPORTED_ENCODINGS_TODO_CHECK})",
    },
    "windows": {
        "shell_sigint": "CTRL + C"
    }
}
