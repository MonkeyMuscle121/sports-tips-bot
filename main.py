import os
from datetime import datetime
import discord
from discord.ext import commands
import logging
import asyncio

# xAI SDK
from xai_sdk import AsyncClient
from xai_sdk.chat import user, system

load_dotenv = __import__("dotenv").load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

LOADING_MESSAGES = [
    "🔍 Loading tips... hold tight 😂",
    "🔍 Fetching fresh picks...",
]

def get_random_loading_message():
    import random
    return random.choice(LOADING_MESSAGES)

async def get_sports_tips():
    try:
        async with asyncio.timeout(50):
            client = AsyncClient(api_key=XAI_API_KEY, timeout=45)
            chat = client.chat.create(
                model="grok-4.20-reasoning",
                temperature=0.7,
                max_turns=3,
            )
            
            prompt = "Give 4 good varied hot tips from different sports for the next few days. Be savage and funny."
            
            chat.append(system("You are a savage, cheeky AI betting bot. Be brutally funny."))
            chat.append(user(prompt))
            response = await chat.sample()
            
            return response.content[:3900]
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return "❌ Failed to fetch tips. Try again in 20 seconds."

@bot.tree.command(name="tips", description="Get hot tips")
async def hot_tips(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    status_msg = await interaction.followup.send(get_random_loading_message())
    
    display = await get_sports_tips()

    embed = discord.Embed(
        title="🔥 Top Hot Tips",
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
