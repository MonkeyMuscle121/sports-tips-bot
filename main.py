import discord
from discord import app_commands
from discord.ui import Select, View
import os
import asyncio
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class SportSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Football", value="football", emoji="⚽"),
            discord.SelectOption(label="Basketball", value="basketball", emoji="🏀"),
            discord.SelectOption(label="Boxing", value="boxing", emoji="🥊"),
            discord.SelectOption(label="Tennis", value="tennis", emoji="🎾"),
            discord.SelectOption(label="Darts", value="darts", emoji="🎯"),
            discord.SelectOption(label="UFC", value="ufc", emoji="🥋"),
        ]
        super().__init__(placeholder="Choose a sport for hot tips", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        sport = self.values[0]
        await interaction.response.edit_message(
            content="**Loading Results from Grok Ai** ⏳ (up to 1 min)", 
            view=None
        )
        
        try:
            from sports_data import get_upcoming_events
            from grok_tips import generate_hot_tips
            
            events = await get_upcoming_events(sport)
            if not events or len(events) == 0:
                await interaction.followup.send(f"No upcoming events found in the next 48 hours for {sport}.")
                return
                
            tips = await generate_hot_tips(sport, events)
            
            embed = discord.Embed(
                title=f"🔥 4 Hot Tips — {sport.upper()} (Next 48h)",
                color=0xFFD700,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Powered by Grok AI • Data from API-Football & TheSportsDB")
            
            for i, tip in enumerate(tips, 1):
                embed.add_field(
                    name=f"Tip #{i} — {tip.get('match', 'Event')}",
                    value=f"**Recommendation:** {tip.get('tip', 'N/A')}\n\n**Savage Write-up:**\n{tip.get('writeup', 'No write-up available.')}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Error in tips callback: {e}")
            await interaction.followup.send(f"❌ Error generating tips: {str(e)[:500]}")

@tree.command(name="tips", description="Get 4 savage Grok AI hot tips for a sport (next 48 hours)")
async def tips(interaction: discord.Interaction):
    view = View(timeout=120)
    view.add_item(SportSelect())
    await interaction.response.send_message("Select a sport for Grok-powered savage tips:", view=view, ephemeral=False)

@client.event
async def on_ready():
    try:
        await tree.sync(guild=None)  # Global + guild commands
        print(f'✅ Bot is ready as {client.user}! Global commands synced.')
    except Exception as e:
        print(f"Sync warning: {e}")

if __name__ == "__main__":
    client.run(os.getenv('DISCORD_TOKEN'))
