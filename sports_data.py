import os
import requests
from datetime import datetime, timedelta
import logging

FOOTBALL_KEY = os.getenv('FOOTBALL_DATA_KEY')
SPORTSDB_KEY = os.getenv('SPORTS_API_KEY')

async def get_upcoming_events(sport: str, limit: int = 20):
    now = datetime.utcnow()
    end_time = now + timedelta(hours=48)
    events = []
    sport_lower = sport.lower()

    try:
        if sport_lower == "football":
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': FOOTBALL_KEY}
            params = {'from': now.strftime('%Y-%m-%d'), 'to': end_time.strftime('%Y-%m-%d')}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                for f in resp.json().get('response', [])[:limit]:
                    home = f.get('teams', {}).get('home', {}).get('name', 'TBD')
                    away = f.get('teams', {}).get('away', {}).get('name', 'TBD')
                    events.append({
                        'match': f"{home} vs {away}",
                        'date': f.get('fixture', {}).get('date'),
                        'league': f.get('league', {}).get('name', '')
                    })

        else:
            # TheSportsDB for other sports
            league_map = {"ufc": "4443", "basketball": "4387", "boxing": "4400", "tennis": "4396", "darts": "4420"}
            lid = league_map.get(sport_lower, "4328")
            
            urls = [
                f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnextleague.php?id={lid}",
                f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnext.php?id=133602"
            ]
            for url in urls:
                resp = requests.get(url, timeout=12)
                if resp.status_code == 200:
                    for e in resp.json().get('events', [])[:limit]:
                        ts = e.get('strTimestamp')
                        if ts:
                            try:
                                event_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                if now < event_time < end_time:
                                    events.append({
                                        'match': e.get('strEvent', 'Event'),
                                        'date': ts,
                                        'league': e.get('strLeague', '')
                                    })
                            except:
                                pass

        logging.info(f"✅ Pulled {len(events)} real events for {sport}")
        return events[:limit]

    except Exception as e:
        logging.error(f"Data fetch error: {e}")
        return []
