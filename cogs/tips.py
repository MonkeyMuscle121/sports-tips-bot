import discord
from discord import app_commands
from discord.ext import commands
import os
from openai import AsyncOpenAI
from utils.sports_data import fetch_upcoming_fixtures, search_specific_event

class TipsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncOpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    @app_commands.command(name="tips", description="Get 4 hot tips for a sport")
    @app_commands.describe(sport="football, basketball, tennis, etc.")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        events = await fetch_upcoming_fixtures(sport)
        
        if not events:
            await interaction.followup.send(f"❌ Sorry, {sport} is not supported yet.")
            return

        events_str = "\n".join([f"{e['home']} vs {e['away']} - {e['league']} @ {e['datetime']}" for e in events])
        
        prompt = f"""You are a sharp sports analyst.
Use ONLY these upcoming {sport} events:

{events_str}

Give EXACTLY 4 hot tips on DIFFERENT events.
Use bullet list. Short reasoning + confidence."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.7
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Analysis failed: {str(e)[:100]}"

        embed = discord.Embed(title=f"🔥 4 Hot {sport.capitalize()} Tips", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="event_tips", description="Get 4 hot tips for one specific match")
    @app_commands.describe(match="e.g. Manchester United vs Liverpool")
    async def event_tips(self, interaction: discord.Interaction, match: str):
        await interaction.response.defer()
        
        event = await search_specific_event(match)
        if not event:
            await interaction.followup.send("❌ Could not find that upcoming match.")
            return
        
        prompt = f"""Analyze this upcoming match:
{event['home']} vs {event['away']} ({event['league']}) at {event['datetime']}

Give exactly 4 sharp hot tips with short reasoning."""

        try:
            response = await self.client.chat.completions.create(
                model="grok-4.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.7
            )
            tips = response.choices[0].message.content
        except Exception as e:
            tips = f"Error: {str(e)[:100]}"

        embed = discord.Embed(title=f"🎯 Tips: {event['home']} vs {event['away']}", description=tips, color=0xffaa00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
