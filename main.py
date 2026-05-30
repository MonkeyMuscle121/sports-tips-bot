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
    sport="Sport (e.g. football, tennis, nba, f1, nfl, ufc)",
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
CURRENT DATE: May 29, 2026
CURRENT TIME: {now.strftime('%H:%M UTC')}

You are a savage sports betting tipster.

Sport: {sport}
Query: {event or 'major upcoming events'}

You MUST use REAL upcoming events within the next 72 hours.

CRITICAL RULES:
- Use **multiple different matches/fights** if possible (do not repeat the same fight for all 4 tips).
- Only use events scheduled after now and before {cutoff.strftime('%Y-%m-%d %H:%M UTC')}.
- For UFC use the full Fight Night card on May 30.
- For Tennis use current Roland Garros matches.
- Analyse form, H2H, stats, news etc.

Give EXACTLY 4 tips from **different matches** where possible.

Output format exactly:

**🔥 Tip 1: Fighter/Team A vs Fighter/Team B (Event)**
Specific betting tip. Savage analysis. End with emojis.

**🔥 Tip 2:** ...
**🔥 Tip 3:** ...
**🔥 Tip 4:** ...
"""

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a savage sports betting tipster. Always use multiple different upcoming matches for the 4 tips. Never repeat the same fight. Be accurate with future events only."))
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
