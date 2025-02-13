import argparse
import sys
from tempfile import template
from utils import Logger
import utils.scanner as sc
import utils.apkstore as store
import utils.apkfile as apkfile
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait

from utils.platinmods import post_to_platinmods
from utils.uploader import upload_to_fileupload, upload_to_modsfire

parser = argparse.ArgumentParser(
    prog="autom8",
    description="Automate the mod stuffs",
    epilog="Author: @rohitaryal",
)

parser.add_argument('-d', '--directory', help="Upload files from this directory")
parser.add_argument('-p', '--profile', help="Use specific profile directory, default: ./profile")
parser.add_argument('-t', '--timeout', help="Timeout for chrome to cancel all plans", type=int)

args = parser.parse_args()
source_dir = args.directory
chrome_profile = args.profile or "./profile"
timeout = args.timeout or 400

if not source_dir:
    parser.print_help()
    sys.exit(-1)

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={chrome_profile}")
options.add_argument(f"--profile-directory=Default")

Logger.info("Starting chrome")
driver = uc.Chrome(options=options, headless=False)
wait = WebDriverWait(driver=driver, timeout=400, poll_frequency=1)

file_list = sc.scan_apps_in_dir(source_dir)

for file in file_list:
    link1 = upload_to_modsfire(driver, wait, file)
    link2 = upload_to_fileupload(driver, wait, file)

    if not link1:
        link1 = Logger.input("Link 1")

    if not link2:
        link2 = Logger.input("Link 2")

    if input("Continue: ").strip() == "n":
        break

    apk_file_details = apkfile.get_detail_from_file(file)
    apk_store_details = {}

    if apk_file_details is None:
        Logger.error(f"Failed to find store details for {file}")

        apk_store_details = store.find(Logger.input("Keyword to search"))
    else:
        apk_store_details = store.get(apk_file_details['PACKAGE_NAME'])

    if apk_store_details is None:
        apk_store_details = {
            'input': Logger.input("App Name"),
            'version': Logger.input("App Version"),
            'icon': Logger.input("App Icon"),
            'url': Logger.input("Store URL"),
            'features': ", ".split(Logger.input("Features[Seperated by ', ']")),
        }

    if not 'features' in apk_store_details:
        apk_store_details['features'] = 'Premium Unlocked'

    post_to_platinmods(
        driver=driver,
        wait=wait,
        app_name = apk_store_details['title'],
        app_version = apk_store_details['version'],
        app_icon=apk_store_details['icon'],
        app_link=apk_store_details['url'],
        app_features=apk_store_details['features'],
        link_1=link1,
        link_2=link2,
        template_path=template,
    )

    if Logger.input("Continue") == 'n':
        break


driver.quit()
