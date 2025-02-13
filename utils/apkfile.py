import os
from .logger import Logger
from apkutils import APK

def get_detail_from_file(path: str):
    if not os.path.isfile(path):
        raise Exception(f"Invalid path or not an permitted file type: {path}")

    try:
        with APK.from_file(path) as apk:
            return {
                "PACKAGE_NAME": apk.get_package_name(),
                "APP_VERSION": apk._version_name,
                "APP_CODE": apk._version_code,
            }
    except:
        Logger.error(f"Failed to get apk detail: {path}")

if __name__ == "__main__":
    args = __import__('sys').argv

    try:
        print(get_detail_from_file(args[1]))
    except:
        print("Usage: python3 apkfile.py FILEPATH")

__all__ = ['get_detail_from_file']
