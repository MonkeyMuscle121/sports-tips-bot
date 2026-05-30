import aiohttp
from datetime import datetime, timedelta
import pytz

# Free API - good for major football leagues
API_KEY = API_KEY = os.getenv("FOOTBALL_DATA_KEY")
BASE_URL = "https://api.football-data.org/v4"

async def fetch_upcoming_fixtures(sport: str, hours: int = 48):
    """Fetch upcoming football matches for next 48h using football-data.org"""
    if sport.lower() not in ["football", "soccer"]:
        return []  # For now we focus on football (expand later)
    
    events = []
    now = datetime.now(pytz.utc)
    cutoff = now + timedelta(hours=hours)
    
    headers = {"X-Auth-Token": API_KEY}
    
    async with aiohttp.ClientSession() as session:
        # Get matches from major competitions
        competitions = ["PL", "CL", "BL", "SA", "PD", "FL1"]  # Premier, Champions, Bundesliga, etc.
        
        for comp in competitions:
            url = f"{BASE_URL}/competitions/{comp}/matches"
            async with session.get(url, headers=headers) as resp:
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
    return events[:15]  # Keep prompt small

async def search_specific_event(query: str):
    """Search for a specific upcoming match"""
    # Simple fallback - for now use broad search, improve later
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}/matches"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
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
                if query.lower() in f"{home} vs {away}".lower():
                    utc_time = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                    if utc_time > now:
                        return {
                            "home": home,
                            "away": away,
                            "league": m["competition"]["name"],
                            "datetime": utc_time.strftime("%Y-%m-%d %H:%M UTC")
                        }
    return None
