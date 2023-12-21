from datetime import datetime
from bs4 import BeautifulSoup
import pytz
import requests

def get_daily_leetcode_question():
    url = 'https://leetcode.com/problemset/'

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the LeetCode page")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    tz = pytz.timezone('UTC')
    current_date = datetime.now(tz).strftime('%Y-%m-%d')
    print(current_date)

    for a in soup.find_all('a', href=True):
        if 'envType=daily-question' in a['href'] and f'envId={current_date}' in a['href']:
            daily_question_url = 'https://leetcode.com' + a['href']
            realurl,_ = daily_question_url.split("?")
            return realurl

    print("No daily question found for today.")
    return None