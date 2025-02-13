from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait

from .logger import Logger

selectors = {
    "input_file": "input[type='file']",
    "modsfire_url_of_file": "tbody > tr > td:nth-child(7) > a",
    "modsfire_attribute_for_url": "data-clipboard-text",
    "fileupload_checkbox": "input[type='checkbox']",
    "fileupload_submit_btn": "button[name='upload']",
    "fileupload_copy_btn": ".btn.icon-btn.link-secondary",
    "fileupload_text_area": "textarea",
}

def upload_to_modsfire(driver: uc.Chrome, wait: WebDriverWait, file_path: str) -> str | None:
    driver.get("https://modsfire.com/upload")

    Logger.log(f"Waiting for {selectors['input_file']}")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['input_file'])))

    Logger.log(f"Found Element")
    file_input = driver.find_element(uc.By.CSS_SELECTOR, selectors['input_file'])

    Logger.log(f"Sending file: {file_path} to form")
    file_input.send_keys(file_path)

    Logger.info("Waiting for file to be uploaded")
    wait.until(lambda _: driver.title == 'ModsFire - Files')

    Logger.info("File uploaded successfully")

    Logger.log(f"Waiting for {selectors['modsfire_url_of_file']}")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['modsfire_url_of_file'])))

    Logger.log(f"Found Element")
    url_anchor = driver.find_element(uc.By.CSS_SELECTOR, selectors['modsfire_url_of_file'])

    url_value = url_anchor.get_attribute(selectors['modsfire_attribute_for_url'])

    Logger.info(f"Modsfire Link: {url_value}")

    return url_value


def upload_to_fileupload(driver: uc.Chrome, wait: WebDriverWait, file_path: str) -> str | None:
    driver.get("https://www.file-upload.org/upload")

    Logger.log(f"Waiting for {selectors['input_file']}")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['input_file'])))


    Logger.log(f"Found Element")
    file_input = driver.find_element(uc.By.CSS_SELECTOR, selectors['input_file'])

    Logger.log(f"Sending file: {file_path} to form")
    file_input.send_keys(file_path)

    Logger.log(f"Waiting for {selectors['fileupload_checkbox']}")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['fileupload_checkbox'])))

    Logger.log("Found Element")
    checkbox = driver.find_element(uc.By.CSS_SELECTOR, selectors['fileupload_checkbox'])

    Logger.log("Clicking over the checkbox")
    driver.execute_script("arguments[0].click()", checkbox)

    Logger.log(f"Waiting for {selectors['fileupload_submit_btn']}")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['fileupload_submit_btn'])))

    Logger.log("Found Element")
    button = driver.find_element(uc.By.CSS_SELECTOR, selectors['fileupload_submit_btn'])

    Logger.log("Clicking on submit button")
    driver.execute_script("arguments[0].click()", button)

    Logger.log("Waiting for file to be uploaded")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['fileupload_copy_btn'])))

    Logger.log(f"Waiting for {selectors['fileupload_text_area']}")
    wait.until(EC.presence_of_element_located((uc.By.CSS_SELECTOR, selectors['fileupload_text_area'])))

    Logger.log(f"Found element")
    textarea = driver.find_element(uc.By.CSS_SELECTOR, selectors['fileupload_text_area'])

    textarea_value = textarea.get_attribute("value")

    if textarea_value is None:
        Logger.error("Failed to find URL value in File-Upload")
        return None

    textarea_url = textarea_value.strip()

    Logger.info(f"FileUpload Link: {textarea_url}")

    return textarea_url
