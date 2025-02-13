from pathlib import Path
from .logger import Logger

# A format defines useful things in a file name
name_format = ["APP_NAME", "APP_VERSION", "APP_FEATURES", "NOTES"]


def parse_name(path: str) -> dict[str, str]:
    parsed_dict = {}
    splitted_path = Path(path).name.replace(".apk", "").split("_")

    for index, items in enumerate(name_format):
        try:
            parsed_dict[items] = splitted_path[index]
        except IndexError:
            break

    return parsed_dict


def is_parsable_format(path: str) -> bool:
    # TODO: Implement a parsable format checker
    #
    Logger.print(f"File in concern: {path}")
    prompt = Logger.input("Does this look parsable [y/n]")

    if prompt == "n":
        return False
    return True


if __name__ == "__main__":
    args = __import__('sys').argv

    try:
        file_name = args[1]
        print(parse_name(file_name))
    except IndexError:
        print("python nameparser.py FILENAME")
