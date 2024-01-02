import json
import os
import psycopg2
import pytz
import discord
from dotenv import load_dotenv
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from dailyscraper import get_daily_leetcode_question

async def scheduled_task(bot):
    url = get_daily_leetcode_question()
    message = f"Today's Daily LeetCode Question: {url}" if url else "Today's Daily LeetCode Question Not Found."

    for guild_id, channel_id in channel_config.items():
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            print(f"Channel not found in guild {guild_id}")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def save_channel_config():
    conn = get_db_connection()
    cur = conn.cursor()
    for guild_id, channel_id in channel_config.items():
        cur.execute("INSERT INTO channel_config (guild_id, channel_id) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = EXCLUDED.channel_id", (guild_id, channel_id))
    conn.commit()
    cur.close()
    conn.close()

def load_channel_config():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS channel_config (guild_id BIGINT PRIMARY KEY, channel_id BIGINT)")
    cur.execute("SELECT guild_id, channel_id FROM channel_config")
    config = {str(row[0]): row[1] for row in cur.fetchall()}
    cur.close()
    conn.close()
    return config

load_dotenv()
DATABASE_URL = os.environ['DATABASE_URL']
TOKEN = os.getenv('DISCORD_TOKEN')
channel_config = load_channel_config()
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
scheduler = AsyncIOScheduler()



@bot.command(name='setchannel')
@commands.has_guild_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel = None):
    if not channel:
        await ctx.send("Please mention a channel.")
        return

    channel_config[str(ctx.guild.id)] = channel.id
    save_channel_config()
    await ctx.send(f"Channel set to {channel.mention} for daily LeetCode questions.")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    scheduler.add_job(scheduled_task, CronTrigger(hour=12, minute=0, second=0, timezone=pytz.utc), args=[bot])
    scheduler.start()

bot.run(TOKEN)
