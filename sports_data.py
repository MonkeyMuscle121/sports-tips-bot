import os
import logging
from datetime import datetime, timedelta

async def get_upcoming_events(sport: str, limit: int = 15):
    """Minimal — Grok will handle event discovery"""
    now = datetime.utcnow()
    end_time = now + timedelta(hours=72)
    
    logging.info(f"Passing {sport} request to Grok for events between {now} and {end_time}")
    return []  # Grok will do the heavy lifting
