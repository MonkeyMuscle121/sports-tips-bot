import aiohttp
from datetime import datetime, timedelta
import pytz
import os

API_KEY = os.getenv("FOOTBALL_DATA_KEY")
BASE_URL = "https://api.football-data.org/v4"

async def fetch_upcoming_fixtures(sport: str, hours: int = 168):  # 7 days
    if sport.lower() not in ["football", "soccer"]:
        return []
    
    events = []
    now = datetime.now(pytz.utc)
    cutoff = now + timedelta(hours=hours)
    
    if not API_KEY:
        return [{"error": "No API key"}]
    
    headers = {"X-Auth-Token": API_KEY}
    
    # Added international competitions
    competitions = ["PL", "CL", "PD", "WC", "EC"]   # Club + International
    
    async with aiohttp.ClientSession() as session:
        for comp in competitions:
            url = f"{BASE_URL}/competitions/{comp}/matches"
            try:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                    matches = data.get("matches", [])
                    
                    for m in matches:
                        try:
                            utc_time = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                            if now < utc_time <= cutoff and m["status"] == "SCHEDULED":
                                events.append({
                                    "home": m["homeTeam"]["name"],
                                    "away": m["awayTeam"]["name"],
                                    "league": m["competition"]["name"],
                                    "datetime": utc_time.strftime("%Y-%m-%d %H:%M UTC")
                                })
                        except:
                            continue
            except:
                continue
    return events[:15]

async def search_specific_event(query: str):
    if not API_KEY:
        return None
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}/matches"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                matches = data.get("matches", [])
                now = datetime.now(pytz.utc)
                
                for m in matches:
                    if m["status"] != "SCHEDULED":
                        continue
                    home = m["homeTeam"]["name"]
                    away = m["awayTeam"]["name"]
                    if query.lower() in f"{home} vs {away}".lower() or query.lower() in home.lower() or query.lower() in away.lower():
                        utc_time = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                        if utc_time > now:
                            return {
                                "home": home,
                                "away": away,
                                "league": m["competition"]["name"],
                                "datetime": utc_time.strftime("%Y-%m-%d %H:%M UTC")
                            }
        except:
            pass
    return None
