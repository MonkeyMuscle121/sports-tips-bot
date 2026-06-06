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
    
    try:
        if sport.lower() == "football":
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': FOOTBALL_KEY}
            params = {'from': now.strftime('%Y-%m-%d'), 'to': end_time.strftime('%Y-%m-%d')}
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json().get('response', [])
                for f in data[:limit]:
                    events.append({
                        'match': f"{f.get('teams',{}).get('home',{}).get('name')} vs {f.get('teams',{}).get('away',{}).get('name')}",
                        'date': f.get('fixture',{}).get('date'),
                        'league': f.get('league',{}).get('name')
                    })
        else:
            # TheSportsDB fallback for other sports
            url = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnext.php?id=4328"  # example league
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get('events', [])[:limit]
                for e in data:
                    events.append({
                        'match': e.get('strEvent', 'Unknown Event'),
                        'date': e.get('strTimestamp')
                    })
        
        logging.info(f"Found {len(events)} events for {sport}")
        return events
    except Exception as e:
        logging.error(f"Data fetch error: {e}")
        return []
