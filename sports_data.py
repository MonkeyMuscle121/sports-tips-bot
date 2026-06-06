import os
import requests
from datetime import datetime, timedelta
import logging

FOOTBALL_KEY = os.getenv('FOOTBALL_DATA_KEY')
SPORTSDB_KEY = os.getenv('SPORTS_API_KEY')

async def get_upcoming_events(sport: str, limit: int = 15):
    """Improved data fetching for all sports"""
    now = datetime.utcnow()
    end_time = now + timedelta(hours=48)
    events = []
    
    try:
        sport = sport.lower()
        
        if sport == "football":
            # API-Football - Excellent coverage
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': FOOTBALL_KEY}
            params = {
                'from': now.strftime('%Y-%m-%d'),
                'to': end_time.strftime('%Y-%m-%d'),
            }
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json().get('response', [])
                for f in data[:limit]:
                    home = f.get('teams', {}).get('home', {}).get('name', 'Unknown')
                    away = f.get('teams', {}).get('away', {}).get('name', 'Unknown')
                    events.append({
                        'match': f"{home} vs {away}",
                        'date': f.get('fixture', {}).get('date'),
                        'league': f.get('league', {}).get('name', ''),
                        'sport': 'football'
                    })
        
        elif sport in ["basketball", "ufc", "boxing", "tennis", "darts"]:
            # TheSportsDB - Try multiple popular leagues/IDs per sport
            league_ids = {
                "basketball": ["4387", "4388"],      # NBA, EuroLeague etc.
                "ufc": ["4390"],                     # UFC related
                "boxing": ["4400"],
                "tennis": ["4396", "4397"],
                "darts": ["4420"]
            }.get(sport, ["4328"])
            
            for lid in league_ids:
                url = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnextleague.php?id={lid}"
                response = requests.get(url, timeout=12)
                
                if response.status_code == 200:
                    data = response.json().get('events', []) or []
                    for e in data[:limit]:
                        try:
                            ts = e.get('strTimestamp')
                            if ts:
                                event_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                if now < event_time < end_time:
                                    events.append({
                                        'match': e.get('strEvent', 'Event'),
                                        'date': ts,
                                        'sport': sport
                                    })
                        except:
                            pass
        else:
            # Generic fallback
            url = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnext.php?id=133602"  # popular team
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get('events', [])
                for e in data:
                    # ... same parsing as above
                    pass
        
        logging.info(f"✅ Fetched {len(events)} events for {sport}")
        return events[:limit]
        
    except Exception as e:
        logging.error(f"❌ Data fetch error for {sport}: {e}")
        return []
