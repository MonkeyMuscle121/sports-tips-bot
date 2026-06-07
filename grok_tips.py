import os
import json
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user
from datetime import datetime

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    client = AsyncClient(api_key=XAI_KEY)
    
    current_date = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    
    prompt = f"""
You are an elite savage sports tipster with real-time knowledge.

Current date/time: {current_date}

Sport: {sport.upper()}

TASK:
1. Identify all REAL upcoming events/matches in the next 72 hours (strictly from now).
2. Analyse form, stats, history, injuries, H2H, betting trends, etc.
3. Select the 4 hottest tips.

Output **ONLY** a valid JSON array with exactly 4 tips. No extra text.

Format:
[
  {{"match": "Exact Event Name", "tip": "Specific recommendation (e.g. Fighter A by Decision, Over 2.5 Goals)", "writeup": "Brutally savage, roasting, funny write-up (2-4 sentences)"}}
]
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. You MUST respond with clean valid JSON array ONLY. No explanations, no markdown."))
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
        logging.error(f"Grok error: {e}")
        return [{"match": "Current Card", "tip": "Loading real events...", "writeup": "Grok analysing live data..."}] * 4
