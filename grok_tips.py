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
    
    events_text = "\n".join([f"- {e.get('match')} on {e.get('date', 'TBD')}" for e in events]) if events else "No events returned from APIs."

    prompt = f"""
You are a STRICT savage sports betting analyst. Current real date/time: {current_date}.

Sport: {sport.upper()}

STRICT RULES - FOLLOW EXACTLY:
- ONLY analyze and tip events that are scheduled in the next 48 hours from now.
- Use ONLY the real events provided below. Do NOT hallucinate or add extra fights.
- If the list is short, still create exactly 4 tips from what's available or note limitations.
- Be brutally savage and roasting in the write-ups.

Real upcoming events (next 48h):
{events_text}

Output **EXACTLY** 4 tips in valid JSON array format only. No extra text, no explanations.

Format:
[
  {{"match": "Exact Event Name", "tip": "Specific recommendation (e.g. Fighter A by Decision)", "writeup": "Savage roasting write-up here"}}
]
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Respond with clean valid JSON array ONLY. Never add extra text."))
        chat.append(user(prompt))
        
        response = await chat.sample()
        content = getattr(response, 'content', str(response))
        
        # Robust JSON extraction
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end] if start >= 0 else content
        tips = json.loads(json_str)
        
        return tips[:4]
        
    except Exception as e:
        logging.error(f"Grok error: {e}")
        return [{"match": "Data Issue", "tip": "Try again soon", "writeup": "Grok had trouble parsing strict 48h window. Check logs."}] * 4
