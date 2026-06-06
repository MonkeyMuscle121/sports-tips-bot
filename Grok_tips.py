import os
import asyncio
from datetime import datetime
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user
import json

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    """Use Grok (via XAI) to analyze events and generate 4 hot tips with savage write-ups"""
    if not events:
        return []
    
    client = AsyncClient(api_key=XAI_KEY)
    
    # Collate events data for Grok
    events_summary = "\n".join([
        f"- {e.get('match')} on {e.get('date')} ({e.get('league', '')})" 
        for e in events[:15]
    ])
    
    prompt = f"""
You are a savage sports betting analyst with deep knowledge.
Sport: {sport.upper()}

Upcoming events in next 48 hours:
{events_summary}

From this data, generate EXACTLY 4 high-confidence "hot tips".
For each tip:
- Match/Event name
- Specific recommendation (e.g. "Over 2.5 goals", "Player A to win", "Moneyline Team B")
- Savage, roasting, funny write-up (2-4 sentences, trash-talk style)

Output ONLY valid JSON array of 4 objects:
[{{
  "match": "...",
  "tip": "Recommendation here",
  "writeup": "Savage text here"
}}]

Be extremely confident and opinionated.
"""
    
    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok, expert savage sports tipster. Always output clean JSON only."))
        chat.append(user(prompt))
        
        response = await chat.sample()
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract JSON
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != -1:
            json_str = content[start:end]
            tips = json.loads(json_str)
        else:
            tips = json.loads(content)
        
        return tips[:4]
        
    except Exception as e:
        logging.error(f"Grok tips error: {e}")
        # Fallback
        return [
            {"match": "Fallback Event", "tip": "Bet on favorite", "writeup": "Grok is processing... placeholder tip."}
            for _ in range(4)
        ]
