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

@tree.command(name="tips", description="Get 4 savage hot tips (next 48h only)")
@app_commands.describe(
    sport="Sport (e.g. football, nba, f1, tennis)",
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
        cutoff = now + timedelta(hours=48)
        
        context = f"""
        Current UTC time: {now.strftime('%Y-%m-%d %H:%M')}
        You MUST consider major real events happening before {cutoff.strftime('%Y-%m-%d %H:%M UTC')}.

        IMPORTANT: Today is around May 29-30 2026. The UEFA Champions League Final (Arsenal vs PSG) is tomorrow May 30. Always include big finals, derbies, or major matches in the next 48 hours.

        Sport: {sport}
        Query: {event or 'major upcoming events'}

        If there are absolutely ZERO real major events, reply with exactly: "NO_UPCOMING_EVENTS"
        Otherwise, ALWAYS give EXACTLY 4 savage hot tips.

        You are a savage, funny, roasting sports tipster. Be brutal and entertaining.
        Use this exact format for each tip:
        **🔥 Tip 1: Team A vs Team B (Competition)**
        Savage description. Add emojis at the end.
        """

        chat = xai_client.chat.create(model="grok-4.3")
        chat.append(system("You are a brutally savage and hilarious sports tipster who always knows current major events."))
        chat.append(user(context))
        
        response = chat.sample()
        ai_output = response.content.strip()

        if "NO_UPCOMING_EVENTS" in ai_output.upper() or "no upcoming" in ai_output.lower():
            embed = discord.Embed(
                title="🏆 SPORTS TIPS — NEXT 48 HOURS",
                description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
                color=0xff4500
            )
            embed.add_field(name="Status", value="❌ There are no options within the next 48 hours.", inline=False)
            embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok")
            await interaction.followup.send(embed=embed)
            return

        # Nice embed matching your screenshot
        embed = discord.Embed(
            title="🏆 SPORTS TIPS — NEXT 48 HOURS",
            description=f"**Sport:** {sport.upper()}\n**Query:** {event or 'Major Events'}",
            color=0xff4500
        )
        embed.add_field(name="Grok's Savage Picks", value=ai_output[:2000], inline=False)
        embed.set_footer(text="🏆 Sports Tips Bot • Powered by Grok • Gamble responsibly")
        embed.timestamp = datetime.utcnow()

        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)[:300]}")

@client.event
async def on_ready():
    print(f'✅ {client.user} is online!')
    await tree.sync()
    print("✅ Commands synced!")

client.run(os.getenv("DISCORD_TOKEN"))
