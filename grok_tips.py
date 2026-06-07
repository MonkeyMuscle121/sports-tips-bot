import os
import json
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user
from datetime import datetime

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    client = AsyncClient(api_key=XAI_KEY)
    
    current_date = datetime.utcnow().strftime("%B %d, %Y")
    events_text = "\n".join([f"- {e.get('match')} ({e.get('league','')}) on {e.get('date','TBD')}" for e in events]) if events else "No events pulled from APIs."

    prompt = f"""
You are an elite savage sports analyst. Current date: {current_date}.

Sport: {sport.upper()}

Real upcoming events in the next 48 hours:
{events_text}

Analyse the provided events deeply (matchups, recent form, H2H if implied, etc.).
Generate **EXACTLY 4 high-confidence hot tips**.

Output ONLY valid JSON array (nothing else):
[
  {{"match": "Exact Match Name", "tip": "Specific recommendation", "writeup": "Savage, roasting, funny 2-4 sentence write-up"}}
]

Be opinionated and brutal.
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Respond with clean valid JSON array ONLY."))
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
        return [{"match": "Data Issue", "tip": "Try Football", "writeup": "Grok analysing real pulled data..."}] * 4
