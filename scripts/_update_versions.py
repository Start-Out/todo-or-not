import os.path
import sys
from datetime import datetime

from todo_or_not import __version__

if __name__ == "__main__":
    args = sys.argv[1:]

    starting_version_string = __version__
    major, minor, patch = starting_version_string.split(".")
    major = int(major)
    minor = int(minor)
    patch = int(patch)

    ############################
    # Increment appropriate version number

    if len(args) == 1:
        if args[0] == "-a":
            major += 1
            minor = patch = 0
        if args[0] == "-i":
            minor += 1
            patch = 0
        if args[0] == "-p":
            patch += 1
    else:
        print(
            "Usage: _update_versions [-a/-i/-p]\n\nM[a]JOR, M[i]NOR, or [p]ATCH version incremented by one"
        )

    today_string = datetime.today().strftime("%Y-%m-%d")
    semver_string = f"{major}.{minor}.{patch}"

    ############################
    # Update __init__.py

    _init_path = os.path.join("..", "todo_or_not", "__init__.py")

    with open(_init_path, "w") as init_file:
        new_contents = f"""import datetime
        
#####################################################
# VITAL: SEE /scripts/_update_versions.py !!!
#
# If updating manually, also consider pyproject.toml
#
#####################################################

__version__ = "{semver_string}"
iso_string = "{today_string}"

version_date = datetime.date.fromisoformat(iso_string)
"""
        init_file.write(new_contents)

    ############################
    # Update pyproject.toml

    _init_path = os.path.join("..", "pyproject.toml")

    with open(_init_path, "r+") as init_file:
        last_line = init_file.tell()
        line = init_file.readline()

        while line != "":
            if line.startswith("version = "):
                init_file.seek(last_line)

                init_file.write(f'version = "{semver_string}"')
                break

            last_line = init_file.tell()
            line = init_file.readline()
