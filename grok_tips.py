import os
import json
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user
from datetime import datetime, timedelta

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    client = AsyncClient(api_key=XAI_KEY)
    
    now = datetime.utcnow()
    current_date = now.strftime("%B %d, %Y at %H:%M UTC")
    cutoff_date = (now + timedelta(hours=72)).strftime("%B %d, %Y")

    prompt = f"""
You are a STRICT, no-hallucination savage sports betting analyst.

CURRENT TIME: {current_date}
MAX CUTOFF: Events must be BEFORE {cutoff_date} (next 72 hours only).

Sport: {sport.upper()}

TASK:
- Find ONLY real, confirmed upcoming events/matches in the next 72 hours.
- If very few events, use whatever real ones exist or note the schedule is quiet.
- Analyse form, stats, history, and current context.
- NEVER use past events or fights scheduled later than the cutoff.

Generate **EXACTLY 4** hot tips.

Output **ONLY** valid JSON array. No other text:
[
  {{"match": "Exact real upcoming event name", "tip": "Specific bet recommendation", "writeup": "Brutally savage, roasting, funny write-up"}}
]
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Respond with clean valid JSON array ONLY. No extra text, no apologies, no explanations."))
        chat.append(user(prompt))
        
        response = await chat.sample()
        content = response.content if hasattr(response, 'content') else str(response)
        
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end] if start >= 0 else content
        
        tips = json.loads(json_str)
        return tips[:4]
        
    except Exception as e:
        logging.error(f"Grok error: {e}")
        return [
            {"match": "Schedule Check", "tip": "Try again soon", "writeup": "The next 72-hour window is currently quiet for major events in this sport."}
        ] * 4
