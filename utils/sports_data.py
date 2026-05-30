import aiohttp
from datetime import datetime, timedelta
import pytz

async def fetch_upcoming_fixtures(sport: str, hours: int = 48):
    sport = sport.capitalize()
    if sport == "Football":
        sport = "Soccer"
    
    events = []
    now = datetime.now(pytz.utc)
    
    async with aiohttp.ClientSession() as session:
        for i in range(3):
            check_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
            url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={check_date}&s={sport}"
            
            async with session.get(url) as resp:
                data = await resp.json()
                day_events = data.get("events", []) or []
                
                cutoff = now + timedelta(hours=hours)
                for e in day_events:
                    try:
                        event_time = datetime.fromisoformat(e["strTimestamp"].replace("Z", "+00:00"))
                        if now < event_time <= cutoff:
                            events.append({
                                "home": e.get("strHomeTeam"),
                                "away": e.get("strAwayTeam"),
                                "league": e.get("strLeague"),
                                "datetime": event_time.strftime("%Y-%m-%d %H:%M UTC")
                            })
                    except:
                        continue
    return events[:20]

async def search_specific_event(query: str):
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchall.php?s={query.replace(' ', '%20')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            events = data.get("event", []) or []
            now = datetime.now(pytz.utc)
            for e in events:
                try:
                    dt = datetime.fromisoformat(e.get("strTimestamp", "").replace("Z", "+00:00"))
                    if dt > now:
                        return {
                            "home": e.get("strHomeTeam"),
                            "away": e.get("strAwayTeam"),
                            "league": e.get("strLeague"),
                            "datetime": dt.strftime("%Y-%m-%d %H:%M UTC")
                        }
                except:
                    continue
    return None
