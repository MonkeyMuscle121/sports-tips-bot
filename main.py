import discord
from discord import app_commands
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user, system

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

xai_client = Client(api_key=os.getenv("XAI_API_KEY"))

@tree.command(name="tips", description="Get 4 savage hot tips (next 48h only) — only works in 🏆-sports-tips")
@app_commands.describe(
    sport="Sport (e.g. football, nba, f1, tennis, nfl)",
    event="Specific event or league (optional)"
)
async def tips(interaction: discord.Interaction, sport: str, event: str = None):
    # === CHANNEL RESTRICTION ===
    channel_name = interaction.channel.name.lower()
    if "sports" not in channel_name or "tips" not in channel_name:
        await interaction.response.send_message(
            "❌ This command only works in the **🏆-sports-tips** channel!\n"
            "Go there and try again 🚀",
            ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)
    
    try:
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=48)
        
        context = f"""
        Current UTC time: {now.strftime('%Y-%m-%d %H:%M')}
        You MUST only consider real events happening before {cutoff.strftime('%Y-%m-%d %H:%M UTC')}.
        
        Sport: {sport}
        Specific request: {event or 'major upcoming events'}
        
        You are an expert savage sports tipster. Be brutally honest, funny, and witty.
        Analyze form, history, weather, stats, injuries, and motivation.
        Give EXACTLY 4 hot tips.
        
        Format exactly like this:
        **🔥 Tip 1: [Short bold title]**
        Savage description with emojis...
        
        Only talk about events in the next 48 hours.
        """
        
        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a brutally honest, savage, and hilarious sports tipster."))
        chat.append(user(context))
        
        response = chat.sample()
        ai_output = response.content
        
        embed = discord.Embed(
            title="🔥 SPORTS TIPS — NEXT 48 HOURS",
            description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
            color=0xff4500
        )
        embed.add_field(name="Grok's Savage Picks", value=ai_output[:1024], inline=False)
        embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok • Gamble responsibly")
        embed.timestamp = datetime.utcnow()
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Oops! Error: {str(e)[:300]}")

@client.event
async def on_ready():
    print(f'✅ {client.user} is online!')
    await tree.sync()
    print("✅ Slash commands synced!")

client.run(os.getenv("DISCORD_TOKEN"))
