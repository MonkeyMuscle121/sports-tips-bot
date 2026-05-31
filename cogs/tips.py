import discord
from discord import app_commands
from discord.ext import commands
import os
from openai import AsyncOpenAI
from utils.sports_data import fetch_upcoming_fixtures

class TipsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncOpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    @app_commands.command(name="tips", description="Get 4 hot tips based on real upcoming events (48h)")
    @app_commands.describe(sport="football, basketball, tennis, etc.")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        events = await fetch_upcoming_fixtures(sport)
        
        if not events:
            await interaction.followup.send(f"❌ No upcoming {sport} events found in the next 48 hours.\n\nTry football or check later.")
            return

        events_str = "\n".join([f"{e['home']} vs {e['away']} - {e['league']} @ {e['datetime']}" for e in events])
        
        prompt = f"""You are an expert sports tipster.
Analyse ONLY these real upcoming {sport} events in the next 48 hours:

{events_str}

Give EXACTLY 4 high quality hot tips on DIFFERENT events.
Vary tip types. Short reasoning."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.75
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Error contacting Grok: {str(e)[:100]}"

        embed = discord.Embed(title=f"🔥 4 Hot {sport.capitalize()} Tips (48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
