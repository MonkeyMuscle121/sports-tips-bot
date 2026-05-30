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
You are a savage, highly accurate sports betting tipster.

CURRENT DATE: May 29, 2026
CURRENT TIME: {now.strftime('%H:%M UTC')}

You MUST ONLY use REAL events scheduled strictly between now and {cutoff.strftime('%Y-%m-%d %H:%M UTC')}.

Sport: {sport}
Query: {event or 'major upcoming events'}

Known real upcoming events right now:
- Arsenal vs PSG - UEFA Champions League Final on May 30
- UFC Fight Night on May 30 (multiple fights on the card)
- Roland Garros (French Open) - multiple matches on May 29, 30, 31

CRITICAL INSTRUCTIONS:
- Strictly future events only within next 72 hours.
- Deeply analyse form, H2H, weather, news, injuries, motivation, stats.
- Give EXACTLY 4 hot betting tips with specific recommendations.
- Never use past or cancelled events.
- If truly nothing, reply "NO_UPCOMING_EVENTS" — otherwise ALWAYS give 4 tips.

Output format exactly:

**🔥 Tip 1: Fighter/Team A vs Fighter/Team B (Event)**
Specific betting tip. Savage, witty, brutal roasting description. End with emojis.

**🔥 Tip 2:** ...
**🔥 Tip 3:** ...
**🔥 Tip 4:** ...
"""

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a savage sports betting tipster. Always provide exactly 4 tips using real upcoming events within the next 72 hours. Never use past events. Be accurate and entertaining."))
        chat.append(user(context))
        
        response = chat.sample()
        ai_output = response.content.strip()

        if "NO_UPCOMING_EVENTS" in ai_output.upper():
            embed = discord.Embed(
                title="🏆 SPORTS TIPS — NEXT 72 HOURS",
                description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
                color=0xff4500
            )
            embed.add_field(name="Status", value="❌ There are no confirmed upcoming events within the next 72 hours.", inline=False)
            embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok")
            embed.timestamp = datetime.utcnow()
            await interaction.followup.send(embed=embed)
            return

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
