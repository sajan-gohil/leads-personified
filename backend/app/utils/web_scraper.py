from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback


def extract_text_with_selenium(url, wait_time=3):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        if not url.startswith('http'):
            url = f'https://{url}'
        driver.get(url)
        # Wait for page to load
        time.sleep(wait_time)
        # Scroll down once
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(wait_time)
        # Optionally, wait for some content to appear
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        # Get all visible text
        text = driver.find_element(By.TAG_NAME, 'body').text
        return text
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None
    finally:
        if driver:
            driver.quit() 