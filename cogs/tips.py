import discord
from discord import app_commands
from discord.ext import commands
import os
from openai import AsyncOpenAI
from datetime import datetime, timedelta
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
        future_date = (now + timedelta(hours=48)).strftime("%B %d, %Y")

        prompt = f"""Today is {current_time}.

Give exactly 4 hot tips for {sport.upper()} events in the next 48 hours (until {future_date}).

Be honest. If few events, use the best available ones. 
Each tip on different event. Short reasoning. Bullet format."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,      # Shorter = faster
                temperature=0.7
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Error generating tips: {str(e)[:100]}"

        embed = discord.Embed(title=f"🔥 4 Hot {sport.upper()} Tips (Next 48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
