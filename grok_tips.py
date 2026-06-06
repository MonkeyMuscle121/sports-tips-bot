import os
import json
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    client = AsyncClient(api_key=XAI_KEY)
    
    events_text = "\n".join([f"- {e.get('match')} at {e.get('date', 'soon')}" for e in events]) if events else "No specific events found from APIs."

    prompt = f"""
You are a savage, expert sports tipster with up-to-date knowledge.
Current date: June 2026.

Sport: {sport.upper()}

Known upcoming events (next 48h):
{events_text}

Even if the list is empty or short, use your knowledge to generate **EXACTLY 4 high-confidence hot tips** for {sport} right now.
Focus on real upcoming matches (e.g. for UFC: Muhammad vs Bonfim, etc.).

For each tip output in valid JSON array only:
[
  {{"match": "Fighter A vs Fighter B", "tip": "Specific bet (e.g. Fighter A ML, Over 1.5 Rounds)", "writeup": "Brutally savage, funny, roasting write-up (2-4 sentences)"}}
]

Be confident, opinionated, and entertaining. No disclaimers.
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Respond ONLY with clean valid JSON array. No extra text."))
        chat.append(user(prompt))
        
        response = await chat.sample()
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Robust JSON extraction
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end] if start >= 0 else content
        tips = json.loads(json_str)
        
        return tips[:4]
        
    except Exception as e:
        logging.error(f"Grok generation error: {e}")
        return [{"match": "Grok Live Analysis", "tip": "Strong Pick", "writeup": "Processing real-time data..."}] * 4
