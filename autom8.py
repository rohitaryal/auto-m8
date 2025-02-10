import os
import argparse
from apkutils import APK
from google_play_scraper import app

################# CONFIGS GO HERE #####################
DEBUG = True



############# Argument Parser Configuration ############
parser = argparse.ArgumentParser(
    prog="autom8",
    description="Automate the mod stuffs",
    epilog="Author: @rohitaryal",
)

parser.add_argument('-m', '--manual', help='Manually enter app detail', action='store_true')
parser.add_argument('-f', '--file', help='Focus only on single file')
parser.add_argument('-d', '--dir', help='Focus on whole directory')
parser.add_argument('-v', '--verbose', help='Print verbose detail', action='store_true')
parser.add_argument('-o', '--output', help='Output path for result')
parser.add_argument('-t', '--template', help='Template file to use')
parser.add_argument('-c', '--credit', help='Username to use as credit')
args = parser.parse_args()


#################### DEFAULTS #######################
built_in_templates = {
    "untested_app": "./templates/untested_app.bb",
    "shared_mod": "./templates/shared_mod.bb",
}

default_username = "me"


########### APK Not Found Exception Class ##############
class APKNotFound(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


    def __str__(self) -> str:
        return f"{self.message}"




############ Invalid App ID Exception Class #############
class InvalidAppID(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message}"




####################### Utils Class #####################
class Utils:
    @staticmethod
    def log(*args):
        if DEBUG:
            print("[+]", "".join(args))

    @staticmethod
    def print(*args):
        print("".join(args))

    @staticmethod
    def error(*args):
        print("[!]", "".join(args))

    @staticmethod
    def info(*args):
        print("[i]", "".join(args))

    @staticmethod
    def prompt(message: str):
        return input("[?] " + message + ": ")

    @staticmethod
    def exec(code: str):
        os.system(code)
    
    @staticmethod
    def readfile(path: str):
        with open(path) as file:
            return file.read()

    @staticmethod
    def appendfile(path: str, content: str):
        with open(path, "a") as file:
            file.write(content)

    @staticmethod
    def bb_format(bb_code: str, pattern: dict):
        for target, replacer in zip(pattern.keys(), pattern.values()):
            bb_code = bb_code.replace(target, str(replacer))

        return bb_code



############### APK Helper Class (Utils) #################
class APKHelper:
    def __init__(self) -> None:
        pass

    """
        Get detail about an apk file represented
        by its path.
    """
    @staticmethod
    def get_file_detail(path: str):
        if not os.path.isfile(path):
            raise APKNotFound(path)

        Utils.log(f"Getting apk detail from: {path}")
        try:
            with APK.from_file(path) as apk:
                return {
                    "app_id": apk.get_package_name(),
                    "version_name": apk._version_name,
                    "version_code": apk._version_code,
                }
        except:
            Utils.error(f"Failed to get apk detail: {path}")
            return None

    """
        Fetch detail about an apk from play store
        using its app id.
    """
    @staticmethod
    def get_store_detail(
        app_id: str,
        lang = None,
        country = None
    ):
        if len(app_id) < 3:
            raise InvalidAppID(f"{app_id}")

        Utils.log(f"Getting app detail from store: {app_id}")
        try:
            return app(
                app_id,
                lang= lang or 'en',
                country= country or 'us'
            )
        except:
            Utils.error(f"Failed to get app detail from store: {app_id}")
            Utils.info("You need to provide info manually.")
            return None

    """
        Scan for apk files in the given path
    """
    @staticmethod
    def scan_apk_files(path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path doesn't exist: {path}")

        apk_list = []
        for current_dir, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".apk") or filename.endswith(".xapk"):
                    apk_list.append(os.path.join(current_dir, filename))
        return apk_list





######################### WORKING BODY HERE ###########################

username = args.credit or "None"
output_path = args.output or "result.bb"
template_path = args.template or built_in_templates["untested_app"]

pattern_target = {
    "{APP_ICON_HERE}": "icon",
    "{APP_LINK_HERE}": "url",
    "{APP_VERSION_HERE}": "version", 
    "{PACKAGE_ID_HERE}": "appId",
    "{APP_DESCRIPTION_HERE}": "description",
    "{APP_NAME_HERE}": "title",
}

if __name__ != "__main__":
    raise Exception("This is not supposed to be used as a library or module")

if not os.path.isfile(template_path):
    raise FileNotFoundError(f"Template file not found: {template_path}")

if args.dir:
    if not os.path.isdir(args.dir):
        raise FileNotFoundError(f"Directory doesn't exist: {args.dir}")

    apk_list = APKHelper.scan_apk_files(args.dir)

    for apk in apk_list:
        apk_detail = APKHelper.get_file_detail(apk)

        if apk_detail is None:
            raise InvalidAppID("No app id obtained. Can't proceed further")

        bb_code = Utils.readfile(template_path)
        store_detail = APKHelper.get_store_detail(apk_detail['app_id'])

        if store_detail is None:
            store_detail = {}
            for key, val in zip(pattern_target.keys(), pattern_target.values()):
                store_detail[val] = Utils.prompt(key)
        else:
            temp = {}
            for key, val in zip(pattern_target.keys(), pattern_target.values()):
                # Limit description to 200 words
                if val == "description":
                    store_detail[val] = store_detail[val][:200]

                temp[key] = store_detail[val]
            store_detail = temp

        store_detail["{FEATURES_HERE}"] = "\n".join(",".split(Utils.prompt("Features (Seperated by commas)")))
        store_detail["{CREDITS_HERE}"] =  Utils.prompt("Credits") or default_username
        store_detail["{NOTES_HERE}"] = Utils.prompt("Notes") or "No Notes"
        store_detail["{DOWNLOAD_LINK1_HERE}"] = Utils.prompt("Download Link 1")
        store_detail["{DOWNLOAD_LINK2_HERE}"] = Utils.prompt("Download Link 2")

        bb_code = Utils.bb_format(bb_code, store_detail)
        Utils.appendfile(output_path, bb_code)