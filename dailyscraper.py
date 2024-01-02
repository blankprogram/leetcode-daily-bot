import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time

def get_daily_leetcode_question():
    url = 'https://leetcode.com/problemset/'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(5) 

        page_source = driver.page_source
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')
    tz = pytz.timezone('UTC')
    current_date = datetime.now(tz).strftime('%Y-%m-%d')

    for a in soup.find_all('a', href=True):
        if 'envType=daily-question' in a['href'] and f'envId={current_date}' in a['href']:
            daily_question_url = 'https://leetcode.com' + a['href']
            realurl, _ = daily_question_url.split("?")
            return realurl

    print("No daily question found for today.")
    return None

