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
    "ko_kr": {
        "issue_body_reference_link": "참조",
        "summary_title": "요약",
        "summary_encoding_unsupported_singular": "지원되지 않는 인코딩(문자)의 이유로 파일이 제외되었습니다",
        "summary_encoding_unsupported_plural": "지원되지 않는 인코딩(문자)의 이유로 여러 파일이 제외되었습니다",
        "info_duplicate_issue_avoided": "정보: 중복 이슈 생성이 방지되었음",
        "error_cannot_specify_ni_xi": "오류: --ni 와 --xi 키워드는 동시에 사용할 수 없습니다",
        "error_is_not_file": "오류: 해당 경로는 파일이 아닙니다",
        "error_todo_ignore_not_found": "오류: .todo-ignore 를 찾을 수 없습니다! -i 를 사용하여 다른 .ignore를 복사하시거나 --force 를 사용하여 .todo-ignore 없이 실행할 수 있습니다(권장되지 않음)",
        "error_todo_ignore_not_supported": f"오류: .todo-ignore 가 지원되지 않는 인코딩(문자)을 사용하고 있거나 존재하지 않습니다! 지원되는 인코딩: {SUPPORTED_ENCODINGS_TODOIGNORE}",
        "error_exceeded_maximum_issues": "오류: 한 번에 생성할 수 있는 최대 깃허브 이슈 생성 횟수를 초과하였으므로 해당 실행을 중단합니다",
        "warning_force_overrides_ignore": "경고: --force 옵션을 지정한다면 해당 실행에서는 .todo-ignore 가 생성한 내용들을 무시할 것입니다 (.todo-ignore 은 여전히 변경되긴 하지만, 그저 사용되지 않을 뿐입니다)",
        "warning_run_with_empty_todo_ignore": "경고: .todo-ignore 이 비어있는 상태로 실행합니다 (만약 파일이 비어있지 않다면, 해당 파일의 인코딩을 확인하십시오), 해당 실행을 취소하고 싶다면 다음을 사용하세요 - ",
        "warning_run_without_todo_ignore": "경고: .todo-ignore 을 제외하고 실행합니다, 해당 실행을 취소하고 싶다면 다음을 사용하세요 -  ",
        "warning_encoding_not_supported": f"경고: 파일이 지원되지 않는 인코딩(문자)을 사용하고 있습니다, .todo-ignore 에 이 파일이 있다고 가정하고 해당 파일을 건너 뛸 것입니다 (지원되는 인코딩: {SUPPORTED_ENCODINGS_TODOIGNORE})",
    },
    "windows": {
        "shell_sigint": "CTRL + C"
    }
}
