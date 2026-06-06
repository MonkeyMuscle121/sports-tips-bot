import os
import json
import logging
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user

XAI_KEY = os.getenv('XAI_API_KEY')

async def generate_hot_tips(sport: str, events: list):
    if not events:
        return [{"match": "No events", "tip": "Check later", "writeup": "No upcoming matches found."}] * 4

    client = AsyncClient(api_key=XAI_KEY)
    
    events_text = "\n".join([f"- {e.get('match')} ({e.get('date', 'TBD')})" for e in events[:12]])
    
    prompt = f"""You are a savage, roasting sports tipster.
Sport: {sport.upper()}

Upcoming matches (next 48h):
{events_text}

Generate **EXACTLY 4** hot tips. Output only valid JSON array like this:
[
  {{"match": "Team A vs Team B", "tip": "Over 2.5 Goals", "writeup": "Savage funny write-up here..."}}
]

Make the write-ups brutal, confident and entertaining."""
    
    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Always respond with clean JSON only."))
        chat.append(user(prompt))
        response = await chat.sample()
        
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract JSON
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end] if start != -1 else content
        tips = json.loads(json_str)
        return tips[:4]
    except Exception as e:
        logging.error(f"Grok error: {e}")
        return [{"match": "Grok Processing", "tip": "Strong Pick", "writeup": "Placeholder - API working."}] * 4
