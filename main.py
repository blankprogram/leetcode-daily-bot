import os
import requests
import pytz
from bs4 import BeautifulSoup
from datetime import datetime
import discord
from dotenv import load_dotenv
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
        ##print(a)
        if 'envType=daily-question' in a['href'] and f'envId={current_date}' in a['href']:
            daily_question_url = 'https://leetcode.com' + a['href']
            realurl,extra = daily_question_url.split("?")
            print(f"Today's Daily Question URL: {realurl}")
            return daily_question_url

    print("No daily question found for today.")
    return None

async def scheduled_task():
    url = get_daily_leetcode_question()
    ##add sending


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
intents = discord.Intents.default()
client = discord.Client(intents=intents)
scheduler = AsyncIOScheduler()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    scheduler.add_job(scheduled_task,CronTrigger(hour=0,minute=0,second=0,timezone=pytz.utc))
    scheduler.start()

client.run(TOKEN)
