import re

from apkutils.apkfile import time
from .logger import Logger
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

selectors = {
    "title_box": ".input.js-titleInput.input--title",
    "app_type_first": ".menuTrigger.menuTrigger--prefix",
    "app_type_second": ".menuPrefix.label.label--orange",
    "bb_if_active": ".fr-command.fr-btn.fr-active",
    "bb_enable_button": "#xfBbCode-1",
    "post_box": "textarea",
    "submit_btn": "button.button--icon.button--icon--write.button--primary.rippleButton",
    "timeout_box": ".overlay",
    "outside_overlay": ".overlay-container.is-active",
    "cancel_button": ".similarthreads-cancel-button",
}

def post_to_platinmods(
    driver: uc.Chrome,
    wait: WebDriverWait,
    app_name: str,
    app_version: str,
    app_icon: str,
    app_link: str,
    app_features: list[str],
    link_1: str,
    link_2: str,
    template_path: str,
):
    Logger.info("Uploading to platinmods.com")

    template = open(template_path).read()
    template = template.replace("app_name", app_name)
    template = template.replace("app_version", app_version)
    template = template.replace("app_icon", app_icon)
    template = template.replace("app_link", app_link)
    template = template.replace("app_features", ", ".join(app_features))
    template = template.replace("link_1", link_1)
    template = template.replace("link_2", link_2)

    driver.get("https://platinmods.com/forums/untested-android-apps.155/post-thread")

    title_box = driver.find_element(uc.By.CSS_SELECTOR, selectors['title_box'])
    title_box.clear()
    title_box.send_keys(f"{app_name} v{app_version} ({app_features[0]})")

    first_type = driver.find_element(uc.By.CSS_SELECTOR, selectors['app_type_first'])
    first_type.click()

    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['app_type_second'])))
    second_type = driver.find_element(uc.By.CSS_SELECTOR, selectors['app_type_second'])
    second_type.click()

    # A random cancel button to bring bb_enable_button to view
    #
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['cancel_button'])))
    temp_element = driver.find_element(uc.By.CSS_SELECTOR, selectors['cancel_button'])
    driver.execute_script("arguments[0].scrollIntoView(true)", temp_element)

    try:
        driver.find_element(uc.By.CSS_SELECTOR, selectors['bb_if_active'])
        Logger.log("BB format already enabled")
    except:
        Logger.log("Enabling BB mode")

        bb_button = driver.find_element(uc.By.CSS_SELECTOR, selectors['bb_enable_button'])
        bb_button.click()

    #Logger.log(f"Waiting for {selectors['post_box']}")
    #wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['post_box'])))
    #
    time.sleep(2)

    #Logger.log("Element found")
    #
    textarea = driver.find_elements(uc.By.CSS_SELECTOR, selectors['post_box'])[1]
    textarea.clear()
    driver.execute_script(f"arguments[0].value = `{template}`", textarea)

    post_button = driver.find_element(uc.By.CSS_SELECTOR, selectors['submit_btn'])
    post_button.click()

    Logger.info("Detecting timeout dialog")
    time.sleep(3)

    try:
        timeout_box = driver.find_element(uc.By.CSS_SELECTOR, selectors['timeout_box'])

        timeout_text = re.search(r"\d+", timeout_box.text)

        if timeout_text:
            timeout_text = int(timeout_text.group(0))
        else:
            # Just wait for 30 seconds
            #
            timeout_text = 100

        Logger.info(f"{timeout_text} seconds timeout detected. Waiting...")

        # This helps to dismiss the overlay
        #
        overlay = driver.find_element(uc.By.CSS_SELECTOR, selectors['outside_overlay'])
        overlay.click()

        time_limit = timeout_text + 10
        i = 0

        while i < time_limit:
            time.sleep(1)
            i += 1
            print(f"[ @ ] Seconds elasped: {i}", end='\r')

        post_button.click()
    except:
        Logger.info("No timeout detected")

    time.sleep(4)
    Logger.info(f"{app_name} uploaded successfully.")
