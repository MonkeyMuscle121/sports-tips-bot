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
        Current date and time: {now.strftime('%Y-%m-%d %H:%M UTC')}
        You MUST ONLY reference REAL upcoming events or matches happening strictly before {cutoff.strftime('%Y-%m-%d %H:%M UTC')}.

        Sport: {sport}
        Query: {event or 'upcoming events'}

        If you cannot confidently identify real upcoming matches for this sport right now, reply with exactly: "NO_UPCOMING_EVENTS"

        Otherwise, give EXACTLY 4 hot betting tips.
        Each tip must include a **specific betting recommendation** (handicap, over/under, winner, etc.).

        Format exactly like this:
        **🔥 Tip 1: Team A vs Team B (Competition)**
        Specific betting tip. Savage, funny, roasting description. End with emojis.

        Do not invent or hallucinate matches. Only use real ones you are confident about.
        """

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a savage sports betting tipster. Be extremely honest and accurate. Never make up matches or fixtures. If you are not sure about current upcoming events, say NO_UPCOMING_EVENTS."))
        chat.append(user(context))
        
        response = chat.sample()
        ai_output = response.content.strip()

        if "NO_UPCOMING_EVENTS" in ai_output.upper() or "cannot confidently" in ai_output.lower():
            embed = discord.Embed(
                title="🏆 SPORTS TIPS — NEXT 72 HOURS",
                description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
                color=0xff4500
            )
            embed.add_field(name="Status", value="❌ No confirmed upcoming events right now.", inline=False)
            embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok")
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="🏆 SPORTS TIPS — NEXT 72 HOURS",
            description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
            color=0xff4500
        )
        embed.add_field(name="Grok's Savage Picks", value=ai_output[:2000], inline=False)
        embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok • Gamble responsibly")
        embed.timestamp = datetime.utcnow()

        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)[:400]}")

@client.event
async def on_ready():
    print(f'✅ {client.user} is online!')
    await tree.sync()
    print("✅ Commands synced!")

client.run(os.getenv("DISCORD_TOKEN"))
