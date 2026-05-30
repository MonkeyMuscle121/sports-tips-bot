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
