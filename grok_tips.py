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
    
    events_text = "\n".join([f"- {e.get('match')} on {e.get('date', 'TBD')}" for e in events]) if events else "No API events found."

    prompt = f"""
You are a STRICT savage sports tipster. Today's date is {current_date}.

Sport: {sport.upper()}

REAL CURRENT UFC CARD (June 6, 2026 - Muhammad vs Bonfim):
- Belal Muhammad vs Gabriel Bonfim (Main Event)
- Brendan Allen vs Edmen Shahbazyan
- Fares Ziam vs Tom Nolan
- Bryce Mitchell vs Victor Henry / Santiago Luna
- Other prelims/main card fights happening TODAY.

STRICT RULES:
- ONLY use fights from the actual current card above.
- Do NOT invent or use future fights (no Islam, no O'Malley, no Shavkat, etc.).
- Generate EXACTLY 4 hot tips from the real card.

Output ONLY valid JSON array. No other text.

[
  {{"match": "Exact Fighter A vs Fighter B", "tip": "Specific bet", "writeup": "Brutally savage roasting write-up"}}
]
"""

    try:
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Respond with clean valid JSON array ONLY. No explanations."))
        chat.append(user(prompt))
        
        response = await chat.sample()
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Force JSON extraction
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end] if start >= 0 else content
        
        tips = json.loads(json_str)
        return tips[:4]
        
    except Exception as e:
        logging.error(f"Grok error: {e}")
        # Hard fallback with real fights
        return [
            {"match": "Belal Muhammad vs Gabriel Bonfim", "tip": "Muhammad by Decision", "writeup": "Bonfim is a hype job getting fed to the king. Bet against the Brazilian and enjoy watching him get outgrinded."},
            {"match": "Brendan Allen vs Edmen Shahbazyan", "tip": "Allen by Submission", "writeup": "Edmen’s chin is made of paper. Brendan will drag him to the mat and choke him out like a training dummy."},
            {"match": "Fares Ziam vs Tom Nolan", "tip": "Ziam by Decision", "writeup": "Nolan is all hype, no finish. Ziam’s technical striking will school him for 3 rounds."},
            {"match": "Bryce Mitchell vs Victor Henry", "tip": "Mitchell by Decision", "writeup": "Bryce is a grappling demon. Henry will get smothered and cry about it after."}
        ]
