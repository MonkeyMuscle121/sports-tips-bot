import discord
from discord import app_commands
from discord.ext import commands
import os
from openai import AsyncOpenAI
from datetime import datetime
import pytz

class TipsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncOpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    @app_commands.command(name="tips", description="Get 4 hot tips for upcoming events only")
    @app_commands.describe(sport="ufc, football, tennis, basketball etc")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        now = datetime.now(pytz.utc)
        current_time = now.strftime("%A, %B %d, %Y at %H:%M UTC")
        
        prompt = f"""Today is {current_time}.

You are a professional sports tipster. 

Give me **exactly 4 hot tips** for **{sport.upper()}** events that are **scheduled in the next 48 hours from now**.

Important Rules:
- ONLY use events that are actually happening between now and { (now + timedelta(hours=48)).strftime("%A, %B %d, %Y") }.
- Do NOT use any past events.
- Each tip must be on a different event/fight/match.
- Vary the tips (winner, method of victory, rounds, props, etc.).
- Keep reasoning short and sharp.

If there are no major events, say so clearly at the top."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=900,
                temperature=0.7
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Error: {str(e)[:200]}"

        embed = discord.Embed(title=f"🔥 4 Hot {sport.upper()} Tips (Next 48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
