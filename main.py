import os
import pytz
import discord
from dotenv import load_dotenv
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from dailyscraper import get_daily_leetcode_question

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
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
scheduler = AsyncIOScheduler()

@bot.command(name='setchannel')
@commands.has_guild_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel = None):
    if not channel:
        await ctx.send("Please mention a channel.")
        return

    channel_config[ctx.guild.id] = channel.id
    await ctx.send(f"Channel set to {channel.mention} for daily LeetCode questions.")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    scheduler.add_job(scheduled_task, CronTrigger(hour=0, minute=15, second=0, timezone=pytz.utc), args=[bot])
    scheduler.start()

bot.run(TOKEN)
