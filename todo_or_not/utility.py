import hashlib
import os
import sys

import todo_or_not
from todo_or_not.localize import LOCALIZE

LOG_LEVEL_NONE = 0
LOG_LEVEL_SUMMARY_ONLY = 1
LOG_LEVEL_NORMAL = 2
LOG_LEVEL_VERBOSE = 3


def print_wrap(
    msg: str, msg_level=LOG_LEVEL_NORMAL, log_level=LOG_LEVEL_NORMAL, file=sys.stdout
):
    if msg_level <= log_level:
        print(msg, file=file)


def version_callback(log_level=LOG_LEVEL_NORMAL):
    print_wrap(
        log_level=log_level,
        msg=f"TODO-Or-Not v{todo_or_not.__version__} ({todo_or_not.version_date})",  # todoon
    )
    sys.exit(0)


def get_todo_ignore_path():  # todoon
    return os.path.join(os.getcwd(), ".todo-ignore")  # todoon


def get_is_debug():
    _debug = os.environ.get("DEBUG", "False").lower()
    if _debug == "true" or _debug == "yes"  or _debug == "y" or _debug == "1":
        return True
    else:
        return False


def get_max_issues():
    _max_issues = os.environ.get("MAXIMUM_ISSUES_GENERATED", "8")

    try:
        max_issues = int(_max_issues)
    except ValueError:
        max_issues = 8

    return max_issues


def get_pertinent_line_limit():
    _pertinent_line_limit = os.environ.get("PERTINENT_LINE_LIMIT", "8")

    try:
        pertinent_line_limit = int(_pertinent_line_limit)
    except ValueError:
        pertinent_line_limit = 8

    return pertinent_line_limit


def get_region(log_level=LOG_LEVEL_NORMAL):
    region = os.environ.get("REGION", "en_us")

    # Validate that we support the region, otherwise default to something we have
    if region not in LOCALIZE:
        print_wrap(
            log_level=log_level,
            msg=f"{LOCALIZE['en_us']['warning_using_default_region']} region",
            file=sys.stderr,
        )
        region = "en_us"

    return region


def get_os(log_level=LOG_LEVEL_NORMAL):
    _os = os.environ.get("OS", "default")
    _os = _os.lower()

    # Validate that we support the region, otherwise default to something we have
    if _os not in LOCALIZE:
        print_wrap(
            log_level=log_level,
            msg=f"{LOCALIZE[get_region()]['warning_using_default_os']} _os",
            file=sys.stderr,
        )
        _os = "default"

    return _os


def sha1_hash(hit_str: str):
    m = hashlib.sha1()
    m.update(bytes(hit_str, "utf-8"))
    return m.hexdigest()


def loc(key: str):
    try:
        localization = LOCALIZE[get_region()][key]
    except KeyError:
        localization = LOCALIZE["en_us"][key]

    return localization

