import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import asyncio

# xAI SDK
from xai_sdk import AsyncClient
from xai_sdk.chat import user, system

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler(timezone="Europe/London")

LOADING_MESSAGES = [
    "🔍 Finding real upcoming events... hold tight 😂",
    "🔍 Fetching fresh tips...",
    "🔍 Loading...",
]

def get_random_loading_message():
    import random
    return random.choice(LOADING_MESSAGES)

async def get_sports_tips(sport: str = None, specific_event: str = None):
    try:
        async with asyncio.timeout(55):
            client = AsyncClient(api_key=XAI_API_KEY, timeout=50)
            chat = client.chat.create(
                model="grok-4.20-reasoning",
                temperature=0.7,
                max_turns=3,
            )
            
            if specific_event:
                prompt = f"Give 3 good tips for this specific event: {specific_event}. Be savage and funny."
            else:
                prompt = "Give 4 good varied hot tips from different sports for the next 72 hours. Be savage and funny."
            
            chat.append(system("You are a savage, cheeky AI betting bot. Only use real upcoming events. Be brutally funny."))
            chat.append(user(prompt))
            response = await chat.sample()
            
            return response.content[:3900]
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return "❌ Failed to fetch tips. Try again in 20 seconds."

@bot.tree.command(name="tips", description="Get 4 hot tips")
async def hot_tips(interaction: discord.Interaction, sport: str = "all"):
    await interaction.response.defer(thinking=True)
    status_msg = await interaction.followup.send(get_random_loading_message())
    
    display = await get_sports_tips(sport)

    embed = discord.Embed(
        title=f"🔥 Top Tips for {sport.replace('_', ' ').title()}",
        description=f"📅 {datetime.now(pytz.timezone('Europe/London')).strftime('%A %d %B %Y %H:%M')} BST",
        color=0xff00ff
    )
    embed.add_field(name="Tips", value=display, inline=False)
    embed.set_footer(text="🔥 For entertainment only • Gamble responsibly • 18+")
    await interaction.followup.send(embed=embed)
    try: await status_msg.delete()
    except: pass

@bot.tree.command(name="tipsevent", description="Get 3 tips for a specific event")
async def tips_event(interaction: discord.Interaction, sport: str, event: str):
    await interaction.response.defer(thinking=True)
    status_msg = await interaction.followup.send(get_random_loading_message())
    
    display = await get_sports_tips(specific_event=event)

    embed = discord.Embed(
        title=f"🎯 3 Tips for: {event}",
        description=f"📅 {datetime.now(pytz.timezone('Europe/London')).strftime('%A %d %B %Y %H:%M')} BST",
        color=0xff00ff
    )
    embed.add_field(name="Tips", value=display, inline=False)
    embed.set_footer(text="🔥 For entertainment only • Gamble responsibly • 18+")
    await interaction.followup.send(embed=embed)
    try: await status_msg.delete()
    except: pass

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is ONLINE!")
    try:
        await bot.tree.sync()
        print("✅ Commands synced")
    except Exception as e:
        print(f"Sync error: {e}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
