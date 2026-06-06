import os
import requests
from datetime import datetime, timedelta
import asyncio
import logging

FOOTBALL_KEY = os.getenv('FOOTBALL_DATA_KEY')
SPORTSDB_KEY = os.getenv('SPORTS_API_KEY')  # TheSportsDB key

async def get_upcoming_events(sport: str, limit: int = 20):
    """Fetch upcoming events in next 48 hours using appropriate API"""
    now = datetime.utcnow()
    end_time = now + timedelta(hours=48)
    
    events = []
    
    try:
        if sport == "football":
            # API-Football fixtures
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': FOOTBALL_KEY}
            params = {
                'from': now.strftime('%Y-%m-%d'),
                'to': end_time.strftime('%Y-%m-%d'),
            }
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json().get('response', [])
                for fixture in data[:limit]:
                    events.append({
                        'id': fixture.get('fixture', {}).get('id'),
                        'match': f"{fixture.get('teams', {}).get('home', {}).get('name')} vs {fixture.get('teams', {}).get('away', {}).get('name')}",
                        'date': fixture.get('fixture', {}).get('date'),
                        'league': fixture.get('league', {}).get('name'),
                        'sport': 'football'
                    })
        else:
            # Other sports - TheSportsDB (basic support)
            url = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsnextleague.php?id=4328"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get('events', []) or []
                for event in data[:limit]:
                    if event.get('strTimestamp'):
                        try:
                            event_time = datetime.fromisoformat(event['strTimestamp'].replace('Z', '+00:00'))
                            if now < event_time < end_time:
                                events.append({
                                    'match': f"{event.get('strHomeTeam')} vs {event.get('strAwayTeam') or event.get('strEvent')}",
                                    'date': event.get('strTimestamp'),
                                    'sport': sport
                                })
                        except:
                            pass
        
        # Filter strictly next 48h
        events = [e for e in events if e.get('date')]
        logging.info(f"Fetched {len(events)} upcoming events for {sport}")
        return events[:limit]
        
    except Exception as e:
        logging.error(f"Error fetching data for {sport}: {e}")
        return []
