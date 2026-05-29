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

@tree.command(name="tips", description="Get 4 savage hot betting tips (next 72h only)")
@app_commands.describe(
    sport="Sport (e.g. football, tennis, nba, f1, nfl)",
    event="Specific event or league (optional)"
)
async def tips(interaction: discord.Interaction, sport: str, event: str = None):
    channel_name = interaction.channel.name.lower()
    if "sports" not in channel_name or "tips" not in channel_name:
        await interaction.response.send_message("❌ This command only works in the **🏆-sports-tips** channel!", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    
    try:
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=72)
        
        context = f"""
You are an expert savage sports betting tipster.

CURRENT DATE: May 29, 2026
CURRENT TIME: {now.strftime('%H:%M UTC')}

You MUST analyse REAL upcoming events in the next 72 hours for the requested sport.

Sport: {sport}
Query: {event or 'major upcoming events'}

Real events happening now:
- UEFA Champions League Final: Arsenal vs PSG on May 30
- Roland Garros (French Open) is in progress with multiple matches on May 29, 30, 31

Rules:
- Find and use real upcoming matches within the next 72 hours.
- Analyse form, head-to-head, weather, player/team news, motivation, stats etc.
- Give EXACTLY 4 hot betting tips with specific recommendations (handicap, over/under, winner, BTTS, correct score range, etc.).
- Be savage, witty, brutal and funny.

Format exactly (no extra text):

**🔥 Tip 1: Team/Player A vs Team/Player B (Event Name)**
Specific betting tip (e.g. Arsenal -1 handicap). Savage analysis and roasting. End with emojis.

**🔥 Tip 2: ...** (do all 4 tips)
"""

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a savage, hilarious, and highly analytical sports betting tipster. Always provide exactly 4 high-quality tips based on real upcoming events. Never say there are no events when major ones exist."))
        chat.append(user(context))
        
        response = chat.sample()
        ai_output = response.content.strip()

        embed = discord.Embed(
            title="🏆 SPORTS TIPS — NEXT 72 HOURS",
            description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
            color=0xff4500
        )
        embed.add_field(name="Grok's Savage Picks", value=ai_output, inline=False)
        embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok • Gamble responsibly")
        embed.timestamp = datetime.utcnow()

        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)[:500]}")

@client.event
async def on_ready():
    print(f'✅ {client.user} is online!')
    await tree.sync()
    print("✅ Commands synced!")

client.run(os.getenv("DISCORD_TOKEN"))
