import discord
from discord import app_commands
from discord.ui import Select, View
import os
import logging
from datetime import datetime

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
            content="**Loading Real Upcoming Events from Grok AI** ⏳ (up to 45 seconds)", 
            view=None
        )
        
        try:
            from sports_data import get_upcoming_events
            from grok_tips import generate_hot_tips
            
            events = await get_upcoming_events(sport)
            tips = await generate_hot_tips(sport, events)
            
            embed = discord.Embed(
                title=f"🔥 4 Hot Tips — {sport.upper()} (Next 72h)",
                color=0xFFD700,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Powered by Grok AI • Strict 72h Window")
            
            for i, tip in enumerate(tips, 1):
                embed.add_field(
                    name=f"Tip #{i} — {tip.get('match', 'Event')}",
                    value=f"**Rec:** {tip.get('tip', 'N/A')}\n\n**Savage Write-up:**\n{tip.get('writeup', 'No write-up')}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Error: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)[:300]}")

@tree.command(name="tips", description="Get 4 savage Grok AI hot tips (next 72 hours)")
async def tips_cmd(interaction: discord.Interaction):
    view = View(timeout=120)
    view.add_item(SportSelect())
    await interaction.response.send_message("Select a sport:", view=view)

@client.event
async def on_ready():
    await tree.sync()
    print(f'✅ Bot ready as {client.user} | Commands synced')

if __name__ == "__main__":
    client.run(os.getenv('DISCORD_TOKEN'))
