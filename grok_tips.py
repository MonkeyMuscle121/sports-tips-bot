import os
import json
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user
from datetime import datetime, timedelta

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    client = AsyncClient(api_key=XAI_KEY)
    
    current_date = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    cutoff_date = (datetime.utcnow() + timedelta(hours=72)).strftime("%B %d, %Y")
    
    prompt = f"""
You are a STRICT savage sports tipster. Current exact date and time: {current_date}.

Sport: {sport.upper()}

CRITICAL RULES (DO NOT BREAK):
- ONLY use events scheduled strictly within the next 72 hours from now.
- Do NOT include any events after {cutoff_date}.
- Do NOT hallucinate big name fights that are not actually happening in the next 72 hours.
- If the schedule is quiet, use only real minor/upcoming events or be honest.
- Analyse real form, stats, and matchups for the actual upcoming events.

Generate **EXACTLY 4** hot tips.

Output ONLY valid JSON array, nothing else:
[
  {{"match": "Exact Event/Fight Name", "tip": "Specific recommendation", "writeup": "Brutally savage, roasting, funny write-up (2-4 sentences)"}}
]
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Respond with clean valid JSON array ONLY. No extra text, no explanations."))
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
        return [
            {"match": "Limited Schedule", "tip": "Check again later", "writeup": "Not many major events in the strict next 72-hour window right now."}
        ] * 4
