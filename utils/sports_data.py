import aiohttp
from datetime import datetime, timedelta
import pytz
import os

API_KEY = os.getenv("SPORTS_API_KEY")
BASE_URL = "https://api.api-sports.io"

async def fetch_upcoming_fixtures(sport: str, hours: int = 48):
    sport_lower = sport.lower().strip()
    events = []
    now = datetime.now(pytz.utc)
    cutoff = now + timedelta(hours=hours)

    headers = {
        "x-apisports-key": API_KEY
    }

    # Map common sports to API-Sports endpoints
    if sport_lower in ["football", "soccer"]:
        endpoint = "football/fixtures"
        params = {"next": "20"}   # Next 20 matches
    elif sport_lower in ["basketball", "nba"]:
        endpoint = "basketball/games"
        params = {"next": "20"}
    elif sport_lower in ["tennis"]:
        endpoint = "tennis/fixtures"
        params = {"next": "10"}
    else:
        # Default to football for now
        endpoint = "football/fixtures"
        params = {"next": "20"}

    async with aiohttp.ClientSession() as session:
        try:
            url = f"{BASE_URL}/{endpoint}"
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    fixtures = data.get("response", [])
                    
                    for f in fixtures:
                        try:
                            # Different structure per sport, handle football mainly for now
                            if sport_lower in ["football", "soccer"]:
                                date_str = f.get("fixture", {}).get("date")
                                home = f.get("teams", {}).get("home", {}).get("name")
                                away = f.get("teams", {}).get("away", {}).get("name")
                                league = f.get("league", {}).get("name", "Football")
                            else:
                                continue  # Expand later
                            
                            if date_str and home and away:
                                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                if now < dt <= cutoff:
                                    events.append({
                                        "home": home,
                                        "away": away,
                                        "league": league,
                                        "datetime": dt.strftime("%Y-%m-%d %H:%M UTC")
                                    })
                        except:
                            continue
        except:
            pass

    # If truly no events found, return empty (no fake data)
    return events[:10]
