from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.influx import get_write_api, get_query_api, get_point
from cleaning.cleaner import clean_event
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/event", tags=["events"])
logger = logging.getLogger(__name__)

class EventRequest(BaseModel):
    user_id: str
    session_id: str
    x: float
    y: float
    timestamp: str
    page: str = "/"

@router.post("/")
async def record_event(req: EventRequest):
    """Receive and write click event to InfluxDB"""
    result = clean_event(req.dict())
    
    if not result['valid']:
        logger.warning(f"[event] rejected: {result['errors']}")
        raise HTTPException(status_code=400, detail=result['errors'])
    
    cleaned = result['cleaned']
    
    try:
        write_api = get_write_api()
        Point = get_point()
        
        point = (
            Point("clicks")
            .tag("user_id", cleaned['user_id'])
            .tag("session_id", cleaned['session_id'])
            .tag("page", cleaned['page'])
            .field("x", cleaned['x'])
            .field("y", cleaned['y'])
            .time(cleaned['timestamp'])
        )
        
        write_api.write(bucket="events", record=point)
        
        logger.info(f"[event] click recorded x={cleaned['x']} y={cleaned['y']} user={cleaned['user_id']}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"[event] influx write error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to write event")

@router.get("/")
async def get_events(sessionId: str, limit: int = 500):
    """Fetch click events for a session from InfluxDB"""
    if not sessionId:
        raise HTTPException(status_code=400, detail="sessionId query param is required")
    
    flux_query = f'''
    from(bucket: "events")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "clicks")
      |> filter(fn: (r) => r.session_id =~ /^{sessionId[:8]}/)
      |> sort(columns: ["_time"])
    '''
    
    try:
        query_api = get_query_api()
        records_stream = query_api.query_stream(query=flux_query, org="analytics")
        
        # Collect events by timestamp (x and y are in separate records)
        events_by_time = {}
        for record in records_stream:
            values = record.values
            time_key = str(values.get('_time'))
            
            if time_key not in events_by_time:
                events_by_time[time_key] = {
                    'timestamp': values.get('_time'),
                    'session_id': values.get('session_id'),
                    'user_id': values.get('user_id'),
                    'page': values.get('page'),
                    'x': None,
                    'y': None
                }
            
            # Fill in x or y based on _field
            field = values.get('_field')
            if field == 'x':
                events_by_time[time_key]['x'] = values.get('_value')
            elif field == 'y':
                events_by_time[time_key]['y'] = values.get('_value')
        
        # Sort by timestamp descending
        rows = sorted(events_by_time.values(), key=lambda e: e['timestamp'], reverse=True)[:limit]
        
        logger.info(f"[event] Found {len(rows)} events for session {sessionId[:8]}")
        return {
            "session_id": sessionId,
            "count": len(rows),
            "events": rows
        }
    except Exception as e:
        logger.error(f"[events] query error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to query events: {str(e)}")

@router.get("/recent")
async def get_recent_events(limit: int = 100):
    """Fetch all recent click events from InfluxDB"""
    flux_query = '''
    from(bucket: "events")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "clicks")
      |> sort(columns: ["_time"], desc: true)
    '''
    
    try:
        query_api = get_query_api()
        records_stream = query_api.query_stream(query=flux_query, org="analytics")
        
        # Collect events by timestamp (x and y are in separate records)
        events_by_time = {}
        for record in records_stream:
            values = record.values
            time_key = str(values.get('_time'))
            
            if time_key not in events_by_time:
                events_by_time[time_key] = {
                    'timestamp': values.get('_time'),
                    'session_id': values.get('session_id'),
                    'user_id': values.get('user_id'),
                    'page': values.get('page'),
                    'x': None,
                    'y': None
                }
            
            # Fill in x or y based on _field
            field = values.get('_field')
            if field == 'x':
                events_by_time[time_key]['x'] = values.get('_value')
            elif field == 'y':
                events_by_time[time_key]['y'] = values.get('_value')
        
        # Sort by timestamp descending and limit
        rows = sorted(events_by_time.values(), key=lambda e: e['timestamp'], reverse=True)[:limit]
        
        return {
            "count": len(rows),
            "events": rows
        }
    except Exception as e:
        logger.error(f"[events/recent] query error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to query events")
