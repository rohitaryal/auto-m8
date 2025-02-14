import argparse
import sys
import string
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

def generate_random_url(base_url: str, length: int = 12) -> str:
    """
    Generates a random URL with a given base URL and a random path of specified length.
    
    :param base_url: The base URL (e.g., "https://www.file-upload.org/")
    :param length: The length of the random path (default is 12 characters)
    :return: A complete URL with a random path
    """
    random_path = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{base_url.rstrip('/')}/{random_path}"

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

for file in file_list:
    print(f"\n\n{Fore.GREEN}=============== NEW THREAD ============== {Fore.RESET}")
    Logger.info(f"File: {file}")

    link1 = "" #Logger.input("Link 1")
    link2 = generate_random_url("https://file-upload.org/")#Logger.input("Link 2")

#    features = Logger.input("Features [Separated by ,]") or "Premium Unlocked"
    features = random.choice(["Pro Unlocked", "Premium Unlocked", "Premium Subscribed", "VIP Unlocked", "Subscribed VIP"])
    features = features.split(", ")

    
    if not link1:
        link1 = upload_to_modsfire(driver, wait, file)
    if not link2:
        link2 = upload_to_fileupload(driver, wait, file)

    file_detail = apkfile.get_detail_from_file(file)

    if file_detail is None:
        continue

    store_detail = store.get(file_detail['PACKAGE_NAME'])

    if store_detail is None:
        store_detail = store.get(store.find(file_detail['PACKAGE_NAME'])[0]['appId'])
        if store_detail is None:
            store_detail = {
                'title': '',
                'version': '',
                'url': '',
                'icon': '',
            }

    post_to_platinmods(
        driver,
        wait,
        link_1 = link1 or "",
        link_2 = link2 or "",
        app_name = store_detail['title'] or Logger.input("App name"),
        app_version = store_detail['version'] or Logger.input("App version"),
        app_link = store_detail['url'] or Logger.input("App link"),
        app_icon = store_detail['icon'] or Logger.input("App icon"),
        app_features =  features,
        template_path = template
   )

driver.quit()
