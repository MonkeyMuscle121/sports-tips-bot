import os
import requests
from datetime import datetime, timedelta
import logging

FOOTBALL_KEY = os.getenv('FOOTBALL_DATA_KEY')
SPORTSDB_KEY = os.getenv('SPORTS_API_KEY')

async def get_upcoming_events(sport: str, limit: int = 15):
    now = datetime.utcnow()
    end_time = now + timedelta(hours=48)
    events = []
    sport = sport.lower()

    try:
        if sport == "football":
            # ... (keep your existing football code)
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': FOOTBALL_KEY}
            params = {'from': now.strftime('%Y-%m-%d'), 'to': end_time.strftime('%Y-%m-%d')}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                for f in resp.json().get('response', [])[:limit]:
                    home = f.get('teams', {}).get('home', {}).get('name', 'TBD')
                    away = f.get('teams', {}).get('away', {}).get('name', 'TBD')
                    events.append({'match': f"{home} vs {away}", 'date': f.get('fixture', {}).get('date')})

        else:
            # Try TheSportsDB + generic search
            urls = [
                f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnext.php?id=133602",  # popular
                f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnextleague.php?id=4390"   # UFC attempt
            ]
            for url in urls:
                resp = requests.get(url, timeout=12)
                if resp.status_code == 200:
                    data = resp.json().get('events', [])[:limit]
                    for e in data:
                        try:
                            ts = e.get('strTimestamp')
                            if ts:
                                event_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                if now < event_time < end_time:
                                    events.append({'match': e.get('strEvent', 'Event'), 'date': ts})
                        except:
                            pass

        logging.info(f"Fetched {len(events)} events for {sport}")
        return events[:limit]

    except Exception as e:
        logging.error(f"Data error for {sport}: {e}")
        return []
