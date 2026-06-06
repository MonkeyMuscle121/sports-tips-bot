import os
import requests
from datetime import datetime, timedelta
import logging

FOOTBALL_KEY = os.getenv('FOOTBALL_DATA_KEY')
SPORTSDB_KEY = os.getenv('SPORTS_API_KEY')

async def get_upcoming_events(sport: str, limit: int = 12):
    now = datetime.utcnow()
    end_time = now + timedelta(hours=48)
    events = []
    sport = sport.lower()

    try:
        if sport == "football":
            # API-Football (reliable)
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': FOOTBALL_KEY}
            params = {'from': now.strftime('%Y-%m-%d'), 'to': end_time.strftime('%Y-%m-%d')}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                for f in resp.json().get('response', [])[:limit]:
                    home = f.get('teams', {}).get('home', {}).get('name', '')
                    away = f.get('teams', {}).get('away', {}).get('name', '')
                    events.append({'match': f"{home} vs {away}", 'date': f.get('fixture', {}).get('date'), 'league': f.get('league', {}).get('name')})

        else:
            # TheSportsDB fallback (limited)
            league_ids = {
                "basketball": ["4387", "4388"],
                "ufc": ["4390", "4328"],
                "boxing": ["4400"],
                "tennis": ["4396"],
                "darts": ["4420"]
            }.get(sport, ["4328"])

            for lid in league_ids:
                url = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnextleague.php?id={lid}"
                resp = requests.get(url, timeout=12)
                if resp.status_code == 200:
                    for e in resp.json().get('events', [])[:limit]:
                        if e.get('strTimestamp'):
                            try:
                                ts = datetime.fromisoformat(e['strTimestamp'].replace('Z', '+00:00'))
                                if now < ts < end_time:
                                    events.append({'match': e.get('strEvent', 'Event'), 'date': e['strTimestamp']})
                            except:
                                pass

        # If very few events (common for UFC/Boxing), return empty so Grok can improvise
        logging.info(f"✅ Raw events fetched: {len(events)} for {sport}")
        return events[:limit]

    except Exception as e:
        logging.error(f"Data fetch error: {e}")
        return []
