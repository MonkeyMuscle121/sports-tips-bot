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
You are a highly accurate, professional savage sports betting tipster.

CURRENT DATE AND TIME: {now.strftime('%Y-%m-%d %H:%M UTC')}

Sport: {sport}
Query: {event or 'major upcoming events'}

Task:
- Identify REAL upcoming matches/fights/events happening strictly within the next 72 hours (before {cutoff.strftime('%Y-%m-%d %H:%M UTC')}).
- For each selected match, deeply analyse form, head-to-head, weather, player/fighter news, injuries, motivation, and key stats.
- Provide EXACTLY 4 hot betting tips with **specific recommendations** (handicap, over/under, moneyline, props, etc.).
- ONLY use real, active, non-cancelled events. Do not hallucinate players or matches.

Be savage, witty, brutal, and entertaining in your descriptions.

Output format exactly (no extra text before or after):

**🔥 Tip 1: Team/Player A vs Team/Player B (Event Name)**
Specific betting tip. Savage analysis and roasting. End with emojis.

**🔥 Tip 2:** ...
**🔥 Tip 3:** ...
**🔥 Tip 4:** ...
"""

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are an expert savage sports betting tipster. Always base tips on real upcoming events only. Never hallucinate fixtures or cancelled matches. Provide exactly 4 tips."))
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
