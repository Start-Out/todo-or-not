import os
import sys

import typer
import typing
import typing_extensions

_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_dir = _script_dir
_todo_ignore_file = os.path.join(_project_dir, ".todo-ignore")


def find_lines(filename: str, *args) -> list[tuple[str, int, [str]]]:
    """
    Finds and returns each line of a file that contains a key
    :param filename: File to open() read-only
    :param args: Keys to check each line for
    :return: List of lines of text and their line number that contain at least one key and the keys each contains
    """
    output = []

    with open(filename, 'r', encoding="UTF-8") as file:
        line_number = 0
        lines = file.readlines()

        for _line in lines:
            _found_keys = []
            for key in args:
                if key.lower() in _line.lower():
                    _found_keys.append(key)

            if len(_found_keys) > 0:
                _hit = (_line, line_number, _found_keys)
                output.append(_hit)

            line_number += 1

    return output


def _print_todo_found(target, hits):
    for hit in hits:
        header = ", ".join(hit[2])
        header = f"[{header}]".upper()
        _pad = 16 - len(header)
        padding = " " * _pad
        header = header + padding

        location = os.path.relpath(target, _project_dir)
        location = f"{location}:{hit[1]}"
        _pad = 16 - len(location)
        padding = " " * _pad
        location = location + padding

        print(f"{header} - {location} - {hit[0].strip()}", file=sys.stderr)


def update_todo_ignore(other_file_names, target_file):
    target_file.write('\n')
    for file_name in other_file_names:
        with open(file_name, "r") as file:
            target_file.writelines(file.read())


def main(ni: typing_extensions.Annotated[typing.Optional[typing.List[str]], typer.Option(
    help="Copy the contents of other files into a new .todo-ignore")] = None,
         xi: typing_extensions.Annotated[typing.Optional[typing.List[str]], typer.Option(
             help="Copy the contents of other files into an existing .todo-ignore")] = None
         , force: bool = False):

    targets = []
    ignored_files = []
    ignored_dirs = []

    if (len(ni) > 0) and (len(xi) > 0):
        print("FATAL: Cannot specify both --ni and --ci.", file=sys.stderr)
        exit(1)
    elif (len(ni) > 0) or (len(xi) > 0):
        if force:
            _option = "--ni" if (len(ni) > len(xi)) else "--ci"
            print("WARNING: --force will ignore the contents of the .todo-ignore generated when you specified",
                  _option,
                  file=sys.stderr)

        mode = "a+" if (len(ni) > len(xi)) else "w"
        _list = ni if (len(ni) > len(xi)) else xi

        with open(os.path.join(_project_dir, ".todo-ignore"), mode, encoding="UTF-8") as new_todo_ignore_file:
            update_todo_ignore(_list, new_todo_ignore_file)

    if not force:
        try:
            with open(_todo_ignore_file, 'r'):
                pass
        except FileNotFoundError:
            print(
                "FATAL: .todo-ignore NOT FOUND! use -i to copy another .ignore OR "
                "--force to run without a .todo-ignore (NOT RECOMMENDED)",
                file=sys.stderr)
            exit(1)

        with open(_todo_ignore_file, 'r') as _ignore:
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

            # Ignore the .todo-ignore itself
            ignored_files.append(os.path.abspath(_ignore.name))
    else:
        print("WARNING: Running without a .todo-ignore (NOT RECOMMENDED), [Ctrl + C] to cancel", file=sys.stderr)

    # Ignore this script
    ignored_files.append(__file__)

    _walk = os.walk(_project_dir)

    for (dirpath, dirnames, filenames) in _walk:
        # Break if an ignored dir
        _ignore_this_dir = False

        for _dir in ignored_dirs:
            if os.path.samefile(dirpath, _dir):
                _ignore_this_dir = True
        if _ignore_this_dir:
            break

        for _file in filenames:
            current = os.path.join(dirpath, _file)

            for i in ignored_files:
                if os.path.samefile(i, current):
                    current = None
                    break

            if current is not None:
                targets.append(current)

    fail = False
    for target in targets:
        hits = find_lines(target, "todo", "fixme")

        if len(hits) > 0:
            fail = True
            _print_todo_found(target, hits)

    if fail:
        print("\n######\nTODO and FIXME check failed, please address the above and try again.\n######\n")
        exit(1)
    else:
        print("\n######\nTODO and FIXME check passed!\n######\n")


if __name__ == "__main__":
    typer.run(main)
