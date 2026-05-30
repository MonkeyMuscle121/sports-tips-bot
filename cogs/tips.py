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

    @app_commands.command(name="tips", description="Get 4 hot tips for a sport (next 48h)")
    @app_commands.describe(sport="football, basketball, tennis, etc.")
    async def sport_tips(self, interaction: discord.Interaction, sport: str):
        await interaction.response.defer()
        
        events = await fetch_upcoming_fixtures(sport)
        if not events:
            await interaction.followup.send(f"❌ No upcoming {sport} events in the next 48 hours.")
            return

        events_str = "\n".join([f"{e['home']} vs {e['away']} - {e['league']} @ {e['datetime']}" for e in events])
        
        prompt = f"""You are a professional sports betting analyst.
Only use these upcoming {sport} matches in the next 48 hours:

{events_str}

Give me EXACTLY 4 high-confidence "hot tips".
- Each tip on a DIFFERENT match.
- Format: bullet list with brief reasoning + confidence (High/Med).
- No past events."""

        response = await self.client.chat.completions.create(
            model="grok-4.3",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        tips = response.choices[0].message.content
        embed = discord.Embed(title=f"🔥 4 Hot {sport.capitalize()} Tips (48h)", description=tips, color=0x00ff00)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="event_tips", description="Get 4 hot tips for one specific match")
    @app_commands.describe(match="e.g. Manchester United vs Liverpool")
    async def event_tips(self, interaction: discord.Interaction, match: str):
        await interaction.response.defer()
        
        event = await search_specific_event(match)
        if not event:
            await interaction.followup.send("❌ Could not find that upcoming match.")
            return
        
        prompt = f"""Analyze this upcoming match ONLY:
{event['home']} vs {event['away']} ({event['league']}) at {event['datetime']}

Give exactly 4 sharp hot tips with short reasoning."""

        response = await self.client.chat.completions.create(
            model="grok-4.3",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )
        
        tips = response.choices[0].message.content
        embed = discord.Embed(title=f"🎯 Tips: {event['home']} vs {event['away']}", description=tips, color=0xffaa00)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TipsCog(bot))
