import os
import sys
import time
import argparse
from apkutils import APK
from google_play_scraper import app
import undetected_chromedriver as uc
from undetected_chromedriver import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

################# CONFIGS GO HERE #####################
DEBUG = True



############# Argument Parser Configuration ############
parser = argparse.ArgumentParser(
    prog="autom8",
    description="Automate the mod stuffs",
    epilog="Author: @rohitaryal",
)

parser.add_argument('-m', '--manual', help='Manually enter app detail', action='store_true')
parser.add_argument('-d', '--dir', help='Focus on whole directory')
parser.add_argument('-v', '--verbose', help='Print verbose detail', action='store_true')
parser.add_argument('-o', '--output', help='Output path for result')
parser.add_argument('-t', '--template', help='Template file to use')
parser.add_argument('-c', '--credit', help='Username to use as credit')
parser.add_argument('-u', '--url', help="URL to open for uploading mod")
parser.add_argument('-p', '--profile', help="Custom profile directory. Default: ./profile")
args = parser.parse_args()


#################### DEFAULTS #######################
built_in_templates = {
    "untested_app": {
        "path": "./templates/untested_app.bb",
        "url": "https://platinmods.com/forums/untested-android-apps.155/post-thread"
    },
    "shared_mod": {
        "path": "./templates/shared_mod.bb",
        "url": ""
    },
}

default_username = "me"
file_hosting = ["https://modsfire.com/upload", "https://www.file-upload.org/upload/"]



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

    @staticmethod
    def get_file_detail(path: str):
        """
            Get detail about an apk file represented
            by its path.
        """
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

    @staticmethod
    def get_store_detail(
        app_id: str,
        lang = None,
        country = None
    ):
        """
            Fetch detail about an apk from play store
            using its app id.
        """
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

    @staticmethod
    def scan_apk_files(path: str):
        """
            Scan for apk files in the given path
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path doesn't exist: {path}")

        apk_list = []
        for current_dir, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".apk") or filename.endswith(".xapk"):
                    apk_list.append(os.path.join(current_dir, filename))
        return apk_list




######################### WORKING BODY HERE ###########################

profile_path = args.profile or "./profile"
username = args.credit or default_username
output_path = args.output or "result.bb"
template_path = args.template or built_in_templates["untested_app"]["path"]
template_url = args.url or built_in_templates["untested_app"]["url"]

pattern_target = {
    "{APP_ICON_HERE}": "icon",
    "{APP_LINK_HERE}": "url",
    "{APP_VERSION_HERE}": "version", 
    "{PACKAGE_ID_HERE}": "appId",
    "{APP_DESCRIPTION_HERE}": "description",
    "{APP_NAME_HERE}": "title",
}

# Don't allow to be imported as module
if __name__ != "__main__":
    raise Exception("This is not supposed to be used as a library or module")


# Check if template path is valid
if not os.path.isfile(template_path):
    raise FileNotFoundError(f"Template file not found: {template_path}")


# --dir or -d is a must flag
if not args.dir:
    parser.print_help()
    sys.exit(-1)


# Check if --dir or -d value is a valid path
if not os.path.isdir(args.dir):
    raise FileNotFoundError(f"Directory doesn't exist: {args.dir}")


# Scan for avalable apk on the path
apk_list = APKHelper.scan_apk_files(args.dir)


# If no apk files found simply raise exception
if len(apk_list) == 0:
    raise APKNotFound(f"No APK found at {args.dir}")


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

    store_detail["{FEATURES_HERE}"] = Utils.prompt("Mod features")
    store_detail["{CREDITS_HERE}"] =  Utils.prompt("Credits") or default_username
    store_detail["{NOTES_HERE}"] = Utils.prompt("Notes") or "No Notes"
    store_detail["{DOWNLOAD_LINK1_HERE}"] = Utils.prompt("Download Link 1")
    store_detail["{DOWNLOAD_LINK2_HERE}"] = Utils.prompt("Download Link 2")


    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument(f"--profile-directory=Default")

    driver = uc.Chrome(options=options, headless=False)
    wait = WebDriverWait(driver=driver, timeout=400, poll_frequency=1)

    

    # Upload files
    for site in file_hosting:
        if store_detail["{DOWNLOAD_LINK1_HERE}"] != "" and store_detail["{DOWNLOAD_LINK2_HERE}"] != "":
            continue

        driver.get(site)
#        time.sleep(100)
        form = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        form.send_keys(apk)
        if "modsfire" in site:
            wait.until(lambda d: driver.title == 'ModsFire - Files')
            time.sleep(4)
            link = driver.find_element(By.CSS_SELECTOR, "tbody > tr > td:nth-child(7) > a")
            store_detail["{DOWNLOAD_LINK1_HERE}"] = link.get_attribute("data-clipboard-text")
        elif "file-upload" in site:
            time.sleep(1)
            checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            checkbox.click()

            button = driver.find_element(By.CSS_SELECTOR, "button[name='upload']")
            button.click()

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.icon-btn.link-secondary")))

            textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
            store_detail["{DOWNLOAD_LINK2_HERE}"] = textarea.get_attribute("value").strip()


    bb_code = Utils.bb_format(bb_code, store_detail)
    Utils.appendfile(output_path, bb_code)

    Utils.log(f"Opening {template_url}")
    driver.get(template_url)

    title_box = driver.find_element(By.CSS_SELECTOR, ".input.js-titleInput.input--title")

    Utils.log("Clearing title box")
    title_box.clear()

    Utils.log("Sending keystrokes to title box")
    title_box.send_keys(store_detail["{APP_NAME_HERE}"] + " v" + store_detail["{APP_VERSION_HERE}"] + " (MOD APK)")

    btn1 = driver.find_element(By.CSS_SELECTOR, ".menuTrigger.menuTrigger--prefix")
    Utils.log("Clicking on btn1")
    btn1.click()

    # Must wait here because html is loaded just now
    time.sleep(1)
    btn2 = driver.find_element(By.CSS_SELECTOR, ".menuPrefix.label.label--orange")
    Utils.log("Clicking on btn2")
    btn2.click()


    # Don't reclick bb code enabler if already enabled
    # ".fr-command.fr-btn.fr-active" class is present if active
    try:
        driver.find_element(By.CSS_SELECTOR, ".fr-command.fr-btn.fr-active")
        Utils.log("BB Code is already active")
    except:
        enable_bb_button = driver.find_element(By.CSS_SELECTOR, "#xfBbCode-1")

        Utils.log("Scrolling to BB Button")
        driver.execute_script("$('.button--icon--cancel')[0].scrollIntoView(true);")

        Utils.log("Enabling BB mode")
        enable_bb_button.click()

        # Must wait here because bb translation to html takes time
        time.sleep(2)


    bb_body_field = driver.find_elements(By.CSS_SELECTOR, "textarea")[1]
    bb_body_field.clear()

    Utils.log("Sending BB content")
    # Not using .send_keys() because '\n' in bb_code is literally taken as Enter command in form
    # This caused the page to redirect, thus this is an easy solution
    driver.execute_script(f"arguments[0].value = `{bb_code}`", bb_body_field)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button.button--icon.button--icon--write.button--primary.rippleButton")
    submit_btn.click()

    time.sleep(5)
    driver.quit()

    print(f"App is uploaded successfully: {apk}")
