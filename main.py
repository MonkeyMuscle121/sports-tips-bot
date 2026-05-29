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
    # Channel restriction
    channel_name = interaction.channel.name.lower()
    if "sports" not in channel_name or "tips" not in channel_name:
        await interaction.response.send_message(
            "❌ This command only works in the **🏆-sports-tips** channel!", 
            ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)
    
    try:
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=72)
        
        context = f"""
You are a professional savage sports betting tipster.

CURRENT DATE AND TIME: {now.strftime('%Y-%m-%d %H:%M UTC')}
You MUST only use REAL upcoming events happening before {cutoff.strftime('%Y-%m-%d %H:%M UTC')}.

Sport requested: {sport}
User query: {event or 'major upcoming events'}

Known real major events right now (May 29 2026):
- UEFA Champions League Final: Arsenal vs PSG (May 30)
- Roland Garros / French Open is currently running with daily matches

Rules:
- ONLY use real upcoming matches within the next 72 hours.
- NEVER use past events.
- NEVER invent or hallucinate matches.
- If you truly cannot find any real upcoming events, reply with exactly "NO_UPCOMING_EVENTS".
- Otherwise ALWAYS give EXACTLY 4 tips.

Each tip must contain:
- A clear betting recommendation (e.g. Arsenal -1 handicap, Over 2.5 goals, Player to win, etc.)

Output format must be exactly like this:

**🔥 Tip 1: Team A vs Team B (Competition Name)**
Specific betting tip. Savage, funny, brutal roasting description. End with relevant emojis.

**🔥 Tip 2: ...**
(and so on for all 4 tips)

Be savage, witty, and entertaining.
"""

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a brutally savage and hilarious sports betting tipster. Always stay accurate to real upcoming events only."))
        chat.append(user(context))
        
        response = chat.sample()
        ai_output = response.content.strip()

        # Check for no events
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

        # Main response
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
        await interaction.followup.send(f"❌ Error generating tips: {str(e)[:500]}")

@client.event
async def on_ready():
    print(f'✅ {client.user} is online!')
    await tree.sync()
    print("✅ Slash commands synced globally!")

client.run(os.getenv("DISCORD_TOKEN"))
