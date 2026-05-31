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

    @app_commands.command(name="tips", description="Get 4 real hot tips for upcoming events")
    @app_commands.describe(sport="ufc, football, tennis, basketball etc")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        data = await fetch_upcoming_fixtures(sport)
        
        prompt = f"""Today is {data['current_time']}.

You are a professional sports betting analyst with up-to-date knowledge.

Give me **exactly 4 high-confidence hot tips** for **{sport.upper()}** events happening in the **next 48 hours**.

Rules:
- Only use events that are realistically scheduled soon.
- Each tip on a different event/fight/match.
- Vary the tip types (winner, method, rounds, player prop, etc.).
- Keep reasoning short and sharp.
- Format as clean bullet list."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=900,
                temperature=0.75
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Error: {str(e)[:200]}"

        embed = discord.Embed(title=f"🔥 4 Hot {sport.upper()} Tips (Next 48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
