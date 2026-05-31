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

    @app_commands.command(name="tips", description="Get 4 hot tips for upcoming events (strict 48h)")
    @app_commands.describe(sport="ufc, football, tennis, basketball etc")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        now = datetime.now(pytz.utc)
        current_time = now.strftime("%A, %B %d, %Y at %H:%M UTC")
        cutoff_date = (now + timedelta(hours=48)).strftime("%A, %B %d, %Y")

        prompt = f"""**STRICT INSTRUCTIONS** - Today is {current_time}.

You are a professional sports tipster. 

Give **exactly 4 hot tips** for **{sport.upper()}** events scheduled **strictly between now and {cutoff_date}** (next 48 hours only).

- Do NOT use any past events.
- If very few major events, be honest and use the best available ones.
- Each tip on a different event.
- Vary the tips (winner, over/under, method, props, etc.).
- Keep reasoning short.

Be accurate. No hallucinations."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Error: {str(e)[:150]}"

        embed = discord.Embed(title=f"🔥 4 Hot {sport.upper()} Tips (Next 48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
