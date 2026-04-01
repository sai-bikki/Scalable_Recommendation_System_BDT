from datetime import datetime
from collections import OrderedDict

# Tracks recently seen events to deduplicate rapid-fire clicks
recent_events = OrderedDict()
DEDUP_WINDOW_MS = 50  # ignore identical clicks within 50ms

def clean_event(raw):
    """Validate and normalize incoming event data before storage"""
    errors = []
    
    # 1. Validate required fields
    if not isinstance(raw.get('user_id'), str) or not raw.get('user_id'):
        errors.append('Invalid user_id')
    if not isinstance(raw.get('session_id'), str) or not raw.get('session_id'):
        errors.append('Invalid session_id')
    if not isinstance(raw.get('x'), (int, float)) or not isinstance(raw.get('y'), (int, float)):
        errors.append('Invalid coordinates')
    
    # 2. Validate coordinate bounds
    if raw.get('x', -1) < 0 or raw.get('x', 10001) > 10000:
        errors.append('x coordinate out of range')
    if raw.get('y', -1) < 0 or raw.get('y', 10001) > 10000:
        errors.append('y coordinate out of range')
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    # 3. Normalize timestamp — use server time if missing or invalid
    try:
        timestamp = datetime.fromisoformat(raw.get('timestamp', '')) if isinstance(raw.get('timestamp'), str) else datetime.now()
    except (ValueError, TypeError):
        timestamp = datetime.now()
    
    # 4. Deduplicate: same user + same pixel within 50ms window
    dedup_key = f"{raw['user_id']}:{int(raw['x'])}:{int(raw['y'])}"
    last_seen = recent_events.get(dedup_key)
    
    current_ms = timestamp.timestamp() * 1000
    if last_seen and current_ms - last_seen < DEDUP_WINDOW_MS:
        return {'valid': False, 'errors': ['Duplicate event (deduplicated)']}
    
    recent_events[dedup_key] = current_ms
    
    # Clean up old entries every 1000 events to prevent memory leak
    if len(recent_events) > 1000:
        cutoff = (datetime.now().timestamp() * 1000) - 5000
        keys_to_remove = [k for k, v in recent_events.items() if v < cutoff]
        for k in keys_to_remove:
            del recent_events[k]
    
    return {
        'valid': True,
        'cleaned': {
            'user_id': raw['user_id'],
            'session_id': raw['session_id'],
            'x': float(raw['x']),
            'y': float(raw['y']),
            'timestamp': timestamp,
            'page': raw.get('page', '/')
        }
    }
