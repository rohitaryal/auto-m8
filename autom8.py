import argparse
import os
import sys
from colorama import Fore
from undetected_chromedriver.patcher import random
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
parser.add_argument('-f', '--template', help="Template to use in platinmods")

args = parser.parse_args()
source_dir = args.directory
chrome_profile = args.profile or "./profile"
timeout = args.timeout or 400
template = args.template or "./templates/untested_app.bb"

if not source_dir:
    parser.print_help()
    sys.exit(-1)

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={chrome_profile}")
options.add_argument(f"--profile-directory=Default")

Logger.info("Starting chrome")
driver = uc.Chrome(options=options, headless=False)
wait = WebDriverWait(driver=driver, timeout=timeout, poll_frequency=1)

file_list = sc.scan_apps_in_dir(source_dir)

for index, file in enumerate(file_list):
    print(f"\n\n{Fore.GREEN}=============== NEW THREAD [{index + 1}/{len(file_list)}] ============== {Fore.RESET}")
    Logger.info(f"File: {file}")

    file_detail = apkfile.get_detail_from_file(file)
    if file_detail is None:
        continue

    store_detail = store.get(file_detail['PACKAGE_NAME'])
    if store_detail is None:
        # Let's be some responsible and just skip if the app is not from store
        #
        continue

    store_detail['version'] = file_detail['APP_VERSION']

    features = random.choice([
            "Pro Unlocked", "Premium Unlocked", "Premium Subscribed", "Premium Unlocked", "Subscribed Premium",
            "Pro Access", "Premium Access", "Premium Access", "Full Premium", 
            "Exclusive Unlocked", "Pro Membership", "Premium Membership", "Premium Membership",
            "Ultimate Unlocked", "All Features Unlocked", "Premium Activated", "Premium Activated",
            "Pro Activated", "Subscribed Pro", "Subscribed Premium", "Premium Subscription",
            "Full Premium", "All Access Unlocked", "Unlimited Access"
        ])
    features = features.split(", ")


    link1 = "" #Logger.input("Link 1")
    link2 = "" #Logger.input("Link 2")    
    if not link1:
        link1 = upload_to_modsfire(driver, wait, file)
    if not link2:
        link2 = upload_to_fileupload(driver, wait, file)

    post_to_platinmods(
        driver,
        wait,
        link_1 = link1 or "",
        link_2 = link2 or "",
        app_name = store_detail['title'],
        app_version = store_detail['version'],
        app_link = store_detail['url'],
        app_icon = store_detail['icon'],
        app_features =  features,
        template_path = template
   )

    os.remove(file)

driver.quit()
