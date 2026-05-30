import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI
from utils.sports_data import fetch_upcoming_fixtures

class TipsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncOpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    @app_commands.command(name="tips", description="Get 4 fresh hot tips for a sport (next 48h)")
    @app_commands.describe(sport="football, basketball, tennis, ufc, etc.")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        events = await fetch_upcoming_fixtures(sport)
        
        if not events:
            await interaction.followup.send(f"❌ No upcoming {sport} events in next 48 hours.")
            return

        events_str = "\n".join([f"{e['home']} vs {e['away']} - {e['league']} @ {e['datetime']}" for e in events])
        
        prompt = f"""You are a sharp sports analyst.
Only use these upcoming {sport} events in the next 48 hours:

{events_str}

Give EXACTLY 4 different hot tips on DIFFERENT events.
Make them fresh and varied. Use bullet points with short reasoning + confidence."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=750,
                temperature=0.8   # Higher temperature = more variety
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Analysis error: {str(e)[:100]}"

        embed = discord.Embed(title=f"🔥 4 Fresh Hot {sport.capitalize()} Tips (48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
