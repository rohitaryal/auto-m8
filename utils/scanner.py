import os

from colorama import Fore
from .logger import Logger
from typing import List

# All functions only work for these filetypes only
permitted_extensions = [".xapk", ".apk"]

def scan_apps_in_dir(path: str) -> List[str]:
    if not os.path.isdir(path):
        raise Exception(f"{path} is not a directory or it doesn't exist")

    found_apk_path = []
    # Recursively find all files in provided directory
    #
    for current_dir, _, filenames in os.walk(path):
        # filenames is a list of all files in `current_dir`
        #
        for filename in filenames:
            # .splitext() splits filename from extension
            # Eg: /path/file.apk becomes ("/path/file", ".apk")
            #
            if os.path.splitext(filename)[-1] in permitted_extensions:
                apk_full_path = os.path.join(current_dir, filename)
                found_apk_path.append(apk_full_path)

    return found_apk_path


def get_app_from_path(path: str) -> str:
    if not os.path.isfile(path):
        raise Exception(f"{path} is not an apk file")

    if os.path.splitext(path)[-1] not in permitted_extensions:
        raise Exception(f"{path} is not a permitted file type");

    return path


def print_file_names(file_list: List[str]):
    for index, filepath in enumerate(file_list):
        if os.path.splitext(filepath)[-1] in permitted_extensions:
            if os.path.exists(filepath):
                Logger.indexed(f"{Fore.GREEN}{filepath}{Fore.RESET}", index)
            else:
                Logger.indexed(f"{Fore.RED}{filepath}{Fore.RESET}", index)
        else:
            Logger.indexed(filepath, index)


def sanitize_filenames(file_paths: List[str], string: str, inplace: bool = False) -> List[str]:
    sanitized_filenames = []

    for index, file_path in enumerate(file_paths):
        if os.path.splitext(file_path)[-1] not in permitted_extensions:
            continue

        sanitized_name = file_path.replace(string, '')
        try:
            os.rename(file_paths[index], sanitized_name)
        except:
            Logger.error(f"Failed to rename {file_paths[index]}")
            continue

        if inplace:
            file_paths[index] = sanitized_name
        else:
            sanitized_filenames.append(sanitized_name)

    return file_paths if inplace else sanitized_filenames
