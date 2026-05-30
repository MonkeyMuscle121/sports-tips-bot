import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    try:
        guild_id = os.getenv("GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            print("✅ Commands synced to guild")
        else:
            await bot.tree.sync()
            print("✅ Commands synced globally")
    except Exception as e:
        print(f"Sync warning: {e}")

async def load_cogs():
    await bot.load_extension("cogs.tips")

import asyncio
asyncio.run(load_cogs())

bot.run(os.getenv("DISCORD_TOKEN"))
