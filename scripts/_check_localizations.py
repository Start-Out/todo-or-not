import sys

from todo_or_not.localize import LOCALIZE

# Simple status check to ensure all localizations are up to date
if __name__ == '__main__':
    dev = set(LOCALIZE["en_us"])

    invalid = {}

    for localization in LOCALIZE:
        if localization in ["en_us", "default", "windows_nt"]:
            continue

        missing = dev - set(LOCALIZE[localization])

        if len(missing) > 0:
            invalid[localization] = missing

    if len(invalid.keys()) > 0:
        print("ERROR: Missing localizations!", file=sys.stderr)

        for localization, missing in invalid.items():
            print(f"Localization {localization} is missing {len(missing)} keys: {missing}", file=sys.stderr)

        sys.exit(1)
