from datetime import datetime
import pytz

async def fetch_upcoming_fixtures(sport: str, hours: int = 48):
    now = datetime.now(pytz.utc)
    return {
        "sport": sport,
        "current_time": now.strftime("%Y-%m-%d %H:%M UTC")
    }
