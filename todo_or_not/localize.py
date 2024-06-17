SUPPORTED_ENCODINGS_TODOIGNORE = ["utf-8", "utf-16"]
SUPPORTED_ENCODINGS_TODO_CHECK = ["utf-8", "utf-16"]

LOCALIZE = {
    "en_us": {
        "general_done": "Done!",
        "issue_body_reference_link": "Reference",
        "summary_title": "Summary",
        "summary_encoding_unsupported_singular": "File skipped due to unsupported encoding",
        "summary_encoding_unsupported_plural": "Files skipped due to unsupported encodings",
        "summary_files_scanned_singular": "File scanned",
        "summary_files_scanned_plural": "Files scanned",
        "summary_issues_generated_singular": "Issue generated",
        "summary_issues_generated_plural": "Issues generated",
        "summary_issues_generated_none": "No issues generated",
        "summary_duplicate_issues_avoided_singular": "Duplicate issue prevented",
        "summary_duplicate_issues_avoided_plural": "Duplicate issues prevented",
        "summary_duplicate_closed_issues_singular": "Previously closed issue detected",
        "summary_duplicate_closed_issues_plural": "Previously closed issues detected",
        "summary_fail_duplicate_closed_issues": "FAIL: Closed duplicate issues detected",
        "summary_found_issues_silent": "INFO: New issues detected, but todoon ran in --silent mode",
        "summary_success": "SUCCESS: No new issues detected",
        "summary_fail_issues_no_silent": "FAIL: New issues detected",
        "info_duplicate_issue_avoided": "INFO: Duplicate issue avoided",
        "error_cannot_specify_ni_xi": "ERROR: Cannot specify both --ni and --xi",
        "error_is_not_file": "ERROR: Specified path is not a file",
        "error_file_already_exists": "ERROR: Specified file already exists",
        "error_no_env": "ERROR: Missing required environment variable",
        "error_gh_issues_read_failed": "ERROR: todoon failed to read from GitHub issues",
        "error_gh_issues_create_failed": "ERROR: todoon failed to create a new GitHub issue",
        "error_todo_ignore_not_found": "ERROR: .todo-ignore NOT FOUND! use -i to copy another .ignore OR --force to run without a .todo-ignore (NOT RECOMMENDED)",
        "error_todo_ignore_not_supported": f"ERROR: .todo-ignore uses unsupported encoding or doesn't exist! Supported encodings: {SUPPORTED_ENCODINGS_TODOIGNORE}",
        "error_exceeded_maximum_issues": "ERROR: Exceeded maximum number of issues for this run, exiting now",
        "warning_force_overrides_ignore": "WARNING: --force will ignore the contents of the .todo-ignore generated when you specified (.todo-ignore will still be changed, just not used)",
        "warning_file_does_not_exist": "WARNING: File doesn't exist",
        "warning_run_with_empty_todo_ignore": "WARNING: .todo-ignore was empty (if the file isn't empty, check its encoding), running anyway. To cancel use ",
        "warning_run_without_todo_ignore": "WARNING: Running without a .todo-ignore, to cancel use ",
        "warning_encoding_not_supported": f"WARNING: File uses unsupported encoding, we will skip it but consider adding to .todo-ignore (Supported encodings: {SUPPORTED_ENCODINGS_TODO_CHECK})",
        "warning_using_default_region": f"WARNING: Unsupported region detected, defaulting to en_us. Detected region:",
        "warning_using_default_os": f"WARNING: Unsupported OS detected, using default tips. Detected OS:",
        "warning_duplicate_closed_issue": f"WARNING: Found an issue that has already been closed",
        "warning_nonissue_mode_closed_duplicate_used": "WARNING: Specified option '--closed-duplicates-fail/-c' will not have any effect when not in '--issue/-i' mode",
        "progress_bar_run_unit": "file",
        "progress_bar_run_desc": "scanning files",
    },
    "ko_kr": {
        "general_done": "끝났습니다!",
        "issue_body_reference_link": "참조",
        "summary_title": "요약",
        "summary_encoding_unsupported_singular": "지원되지 않는 인코딩(문자)의 이유로 파일이 제외되었습니다",
        "summary_encoding_unsupported_plural": "지원되지 않는 인코딩(문자)의 이유로 여러 파일이 제외되었습니다",
        "summary_files_scanned_singular": "하나의 파일을 스캔하였습니다",
        "summary_files_scanned_plural": "여러 개의 파일을 스캔하였습니다",
        "summary_issues_generated_singular": "깃허브 이슈가 생성되었습니다",
        "summary_issues_generated_plural": "깃허브 이슈들이 생성되었습니다",
        "summary_issues_generated_none": "생성된 깃허브 이슈가 없습니다",
        "summary_duplicate_closed_issues_singular": "이전에 닫힌 깃허브 이슈가 탐지되었습니다",
        "summary_duplicate_closed_issues_plural": "이전에 닫힌 깃허브 이슈들이 탐지되었습니다",
        "summary_fail_duplicate_closed_issues": "실패: 이미 닫힌 중복 깃허브 이슈들이 탐지되었습니다",
        "summary_found_issues_silent": "정보: 새 이슈들이 탐지되었으나 현재 todoon은 --silent 모드로 작동되고 있습니다",
        "summary_success": "성공: 탐지된 새 이슈들이 없습니다",
        "summary_fail_issues_no_silent": "실패: 새로운 깃허브 이슈들이 탐지되었습니다",
        "summary_duplicate_issues_avoided_singular": "깃허브 이슈의 중복 생성이 방지되었습니다",
        "summary_duplicate_issues_avoided_plural": "깃허브 이슈들의 중복 생성이 방지되었습니다",
        "info_duplicate_issue_avoided": "정보: 중복 이슈 생성이 방지되었습니다",
        "error_cannot_specify_ni_xi": "오류: --ni 와 --xi 키워드는 동시에 사용할 수 없습니다",
        "error_is_not_file": "오류: 해당 경로는 파일이 아닙니다",
        "error_file_already_exists": "오류: 이미 그 파일이 존재합니다",
        "error_no_env": "오류: 필요한 환경 변수를 찾을 수 없습니다",
        "error_gh_issues_read_failed": "오류: todoon이 깃허브 이슈들을 읽는 것에 실패하였습니다",
        "error_gh_issues_create_failed": "오류: todoon이 새로운 깃허브 이슈를 생성하는 것에 실패하였습니다",
        "error_todo_ignore_not_found": "오류: .todo-ignore 를 찾을 수 없습니다! -i 를 사용하여 다른 .ignore를 복사하시거나 --force 를 사용하여 .todo-ignore 없이 실행할 수 있습니다(권장되지 않음)",
        "error_todo_ignore_not_supported": f"오류: .todo-ignore 가 지원되지 않는 인코딩(문자)을 사용하고 있거나 존재하지 않습니다! 지원되는 인코딩: {SUPPORTED_ENCODINGS_TODOIGNORE}",
        "error_exceeded_maximum_issues": "오류: 한 번에 생성할 수 있는 최대 깃허브 이슈 생성 횟수를 초과하였으므로 해당 실행을 중단합니다",
        "warning_force_overrides_ignore": "경고: --force 옵션을 지정한다면 해당 실행에서는 .todo-ignore 가 생성한 내용들을 무시할 것입니다 (.todo-ignore 은 여전히 변경되긴 하지만, 그저 사용되지 않을 뿐입니다)",
        "warning_file_does_not_exist": "경고: 파일이 존재하지 않습니다",
        "warning_run_with_empty_todo_ignore": "경고: .todo-ignore 이 비어있는 상태로 실행합니다 (만약 파일이 비어있지 않다면, 해당 파일의 인코딩을 확인하십시오), 해당 실행을 취소하고 싶다면 다음을 사용하세요 - ",
        "warning_run_without_todo_ignore": "경고: .todo-ignore 을 제외하고 실행합니다, 해당 실행을 취소하고 싶다면 다음을 사용하세요 -  ",
        "warning_encoding_not_supported": f"경고: 파일이 지원되지 않는 인코딩(문자)을 사용하고 있습니다, .todo-ignore 에 이 파일이 있다고 가정하고 해당 파일을 건너 뛸 것입니다 (지원되는 인코딩: {SUPPORTED_ENCODINGS_TODOIGNORE})",
        "warning_using_default_region": f"경고: 지원되지 않는 지역이 감지되었습니다, en_us(영어)를 기본값으로 둡니다. 감지된 지역:",
        "warning_using_default_os": f"경고: 지원되지 않는 운영체제가 감지되었습니다, 기본 단축키(Ctrl + C)를 사용합니다. 감지된 운영체제:",
        "warning_duplicate_closed_issue": f"경고: 이미 닫힌 깃허브 이슈를 찾았습니다",
        "warning_nonissue_mode_closed_duplicate_used": "경고: 설정한 옵션 '--closed-duplicates-fail/-c'은 '--issue/-i' 모드가 아니라면 아무런 영향을 끼치지 못합니다",
        "progress_bar_run_unit": "파일",
        "progress_bar_run_desc": "파일들을 스캔하고 있음",
    },
    "bu_mm": {
        "general_done": "ပြီးပါပြီ။",
        "issue_body_reference_link": "အညွှန်း",
        "summary_title": "အနှစ်ချုပ် ခေါင်းစဉ်",
        "summary_encoding_unsupported_singular": "ကုဒ်ပြောင်းခြင်းကို ပံ့ပိုးမထားသောကြောင့် ဖိုင်ကို ကျော်သွားသည်",
        "summary_encoding_unsupported_plural": "ကုဒ်ပြောင်းခြင်းကို ပံ့ပိုးမထားသောကြောင့် ဖိုင်များကို ကျော်သွားခဲ့သည်",
        "summary_files_scanned_singular": "ဖိုင်ကို စကင်(န်)ဖတ်ခဲ့ပသည်",
        "summary_files_scanned_plural": "ဖိုင်များကို စကင်(န်)ဖတ်ခဲ့သည်",
        "summary_issues_generated_singular": "ထုတ်ပေးသော ကိစ္စ",
        "summary_issues_generated_plural": "ထုတ်ပေးသော ကိစ္စများ",
        "summary_issues_generated_none": "မည်သည့်ပြဿနာမှ မထုတ်ပေးခဲ့ပါ",
        "summary_duplicate_issues_avoided_singular": "ထပ်တူကိစ္စကို တားဆီးခဲ့သည်",
        "summary_duplicate_issues_avoided_plural": "ထပ်တူကိစ္စများကို တားဆီးခဲ့သည်",
        "summary_duplicate_closed_issues_singular": "ယခင်က ပိတ်ထားသော ပြဿနာကို တွေ့ရှိခဲ့သည်",
        "summary_duplicate_closed_issues_plural": "ယခင်က ပိတ်ထားသော ပြဿနာများကို တွေ့ရှိခဲ့သည်",
        "summary_fail_duplicate_closed_issues": "မအောင်မြင်ပါ- ပိတ်ထားသော မိတ္တူပြဿနာများကို တွေ့ရှိပါသည်",
        "summary_found_issues_silent": "အချက်အလက်- ပြဿနာအသစ်များကို တွေ့ရှိသော်လည်း todoon အသံတိတ် (silent) မုဒ်တွင် လုပ်ဆောင်ခဲ့သည်",
        "summary_success": "အောင်မြင်မှု- ပြဿနာအသစ်မတွေ့ပါ",
        "summary_fail_issues_no_silent": "မအောင်မြင်ပါ- ပြဿနာအသစ်များကို တွေ့ရှိခဲ့သည်",
        "info_duplicate_issue_avoided": "အချက်အလက်- မိတ္တူပွားခြင်းပြဿနာကို ရှောင်ကြဉ်ပါ",
        "error_cannot_specify_ni_xi": "အမှား- _ni နှင့် _xi နှစ်မျိုးလုံးကို သတ်မှတ်၍မရပါ",
        "error_is_not_file": "အမှား- သတ်မှတ်ထားသောလမ်းကြောင်းသည် ဖိုင် မဟုတ်ပါ",
        "error_file_already_exists": "အမှား- သတ်မှတ်ထားသောဖိုင် ရှိနှင့်ပြီးဖြစ်သည်",
        "error_no_env": "အမှား- လိုအပ်သော environment variable ရှာမတွေ့ပါ",
        "error_gh_issues_read_failed": "အမှား- todoon GitHub ပြဿနာများမှ ဖတ်၍မရပါ",
        "error_gh_issues_create_failed": "အမှား- todoon သည် GitHub ပြဿနာအသစ်ကို ဖန်တီး၍မရပါ",
        "error_todo_ignore_not_found": "အမှား- .todo-ignore မတွေ့ပါ။ အခြား .ignore ကိုကူးယူရန် -i ကိုသုံးပါ သို့မဟုတ် .todo-ignore မပါဘဲ run ရန် --force (အကြံပြုမထားပါ)",
        "error_todo_ignore_not_supported": f"အမှား- .todo-ignore သည် ပံ့ပိုးမထားသော ကုဒ်နံပါတ်ကို အသုံးပြုသည် သို့မဟုတ် မရှိပါ။ ပံ့ပိုးထားသော ကုဒ်နံပါတ်များ- {SUPPORTED_ENCODINGS_TODOIGNORE}",
        "error_exceeded_maximum_issues": "အမှား- ဤလုပ်ဆောင်မှုအတွက် ပြဿနာအများဆုံးအရေအတွက်ကို ကျော်သွားသည်၊ ယခုထွက်နေပါသည်",
        "warning_force_overrides_ignore": "သတိပေးချက်- --force သည် သင်သတ်မှတ်လိုက်သောအခါတွင် ထုတ်ပေးသည့် .todo-ignore ၏ အကြောင်းအရာများကို လျစ်လျူရှုလိမ့်မည် (.todo-ignore သည် ပြောင်းလဲနေသေးသည်၊ အသုံးသာမပြုဘဲ)",
        "warning_file_does_not_exist": "သတိပေးချက်- ဖိုင်မရှိပါ။",
        "warning_run_with_empty_todo_ignore": "သတိပေးချက်- .todo-ignore သည် ဗလာဖြစ်သည် (ဖိုင်ဗလာမဟုတ်ပါက ၎င်း၏ကုဒ်နံပါတ်ကို စစ်ဆေးပါ) မည်သို့ပင်ဖြစ်စေ လုပ်ဆောင်နေပါသည်။ အသုံးပြုမှုကို ပယ်ဖျက်ရန် -",
        "warning_run_without_todo_ignore": "သတိပေးချက်- .todo-ignore မပါဘဲ လုပ်ဆောင်နေသည်။ အသုံးပြုမှုကို ပယ်ဖျက်ရန် -",
        "warning_encoding_not_supported": f"သတိပေးချက်- ဖိုင်သည် ပံ့ပိုးမထားသော ကုဒ်နံပါတ်ကို အသုံးပြုသည်၊ ၎င်းကို ကျော်သွားပါမည်၊ သို့သော် .todo-ignore တွင် ထည့်ရန်စဉ်းစားသည် (ပံ့ပိုးပေးထားသော ကုဒ်နံပါတ်များ- {SUPPORTED_ENCODINGS_TODO_CHECK})",
        "warning_using_default_region": f"သတိပေးချက်- ပံ့ပိုးမထားသော ဒေသကို တွေ့ရှိပြီး en_us သို့ ပုံသေသတ်မှတ်ထားသည်။ တွေ့ရှိထားသော ဒေသ-",
        "warning_using_default_os": f"သတိပေးချက်- ပံ့ပိုးမထားသော OS ကို တွေ့ရှိခဲ့ပြီး မပုံသေဖြတ်လမ်းကို အသုံးပြုပါမည်။ တွေ့ရှိထားသော OS-",
        "warning_duplicate_closed_issue": f"သတိပေးချက်- ပိတ်ထားပြီးသော ပြဿနာတစ်ခု တွေ့ရှိပါသည်",
        "warning_nonissue_mode_closed_duplicate_used": "သတိပေးချက်- သတ်မှတ်ထားသော ရွေးချယ်မှု '--closed-duplicates-fail/-c' သည် '--issue/-i' မုဒ်တွင် မရှိ၍ အကျိုးသက်ရောက်မှုမှ မရှိပါ",
        "progress_bar_run_unit": "ဖိုင်",
        "progress_bar_run_desc": "ဖိုင်များကိုစကင်န် ဖတ်နေပါသည်",
    },
    "default": {"shell_sigint": "CTRL + C"},
    "windows_nt": {"shell_sigint": "CTRL + C"},
}
