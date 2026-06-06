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
    
    events_text = "\n".join([f"- {e.get('match')} on {e.get('date', 'soon')}" for e in events]) if events else "No specific events returned from APIs."

    prompt = f"""
You are a strict, savage sports tipster. Current date: {current_date}.

Sport: {sport.upper()}

STRICT RULE: ONLY use matches that are CONFIRMED to happen in the next 48 hours. 
If the provided list is empty or insufficient, say so and generate tips ONLY from the actual main card happening right now (e.g. for UFC on June 6: Muhammad vs Bonfim card).

Provided upcoming events:
{events_text}

Generate **EXACTLY 4** hot tips. Output ONLY a valid JSON array. No extra text.

Format:
[
  {{"match": "Exact Fighter A vs Fighter B", "tip": "Specific recommendation", "writeup": "Savage, roasting, funny write-up"}}
]

Be brutally honest. If no real events in next 48h, use the actual current card.
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. You MUST respond with clean valid JSON array ONLY. No explanations, no markdown, no extra text."))
        chat.append(user(prompt))
        
        response = await chat.sample()
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Strong JSON extraction
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end] if start >= 0 else content
        
        tips = json.loads(json_str)
        return tips[:4]
        
    except Exception as e:
        logging.error(f"Grok error: {e}")
        return [{"match": "Current Card", "tip": "Check live card", "writeup": "Grok had trouble finding strict +48h events. Try Football instead."}] * 4
