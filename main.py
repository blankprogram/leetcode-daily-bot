import os
import requests
import pytz
from bs4 import BeautifulSoup
from datetime import datetime
import discord
from dotenv import load_dotenv
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

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

async def scheduled_task(bot):
    url = get_daily_leetcode_question()
    if url:
        for guild_id, channel_id in channel_config.items():
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f"Today's Daily LeetCode Question: {url}")
            else:
                print(f"Channel not found in guild {guild_id}")

channel_config = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix='!',intents=intents)
scheduler = AsyncIOScheduler()

@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel):
    channel_config[ctx.guild.id] = channel.id
    await ctx.send(f"Channel set to {channel.mention} for daily LeetCode questions.")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    scheduler.add_job(scheduled_task, CronTrigger(hour=0, minute=20, second=0, timezone=pytz.utc), args=[bot])
    scheduler.start()

bot.run(TOKEN)
