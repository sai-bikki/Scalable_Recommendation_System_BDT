/**
 * Data Cleaning Layer
 * Validates and normalizes incoming event data before storage.
 */

// Tracks recently seen events to deduplicate rapid-fire clicks
const recentEvents = new Map();
const DEDUP_WINDOW_MS = 50; // ignore identical clicks within 50ms

function cleanEvent(raw) {
    const errors = [];

    // 1. Validate required fields
    if (!raw.user_id || typeof raw.user_id !== 'string') errors.push('Invalid user_id');
    if (!raw.session_id || typeof raw.session_id !== 'string') errors.push('Invalid session_id');
    if (typeof raw.x !== 'number' || typeof raw.y !== 'number') errors.push('Invalid coordinates');

    // 2. Validate coordinate bounds (must be positive, reasonable screen size)
    if (raw.x < 0 || raw.x > 10000) errors.push('x coordinate out of range');
    if (raw.y < 0 || raw.y > 10000) errors.push('y coordinate out of range');

    if (errors.length > 0) {
        return { valid: false, errors };
    }

    // 3. Normalize timestamp — use server time if missing or invalid
    let timestamp = new Date(raw.timestamp);
    if (isNaN(timestamp.getTime())) {
        timestamp = new Date();
    }

    // 4. Deduplicate: same user + same pixel within 50ms window
    const dedupKey = `${raw.user_id}:${Math.round(raw.x)}:${Math.round(raw.y)}`;
    const lastSeen = recentEvents.get(dedupKey);
    if (lastSeen && timestamp.getTime() - lastSeen < DEDUP_WINDOW_MS) {
        return { valid: false, errors: ['Duplicate event (deduplicated)'] };
    }
    recentEvents.set(dedupKey, timestamp.getTime());

    // Clean up old entries every 1000 events to prevent memory leak
    if (recentEvents.size > 1000) {
        const cutoff = Date.now() - 5000;
        for (const [key, ts] of recentEvents.entries()) {
            if (ts < cutoff) recentEvents.delete(key);
        }
    }

    return {
        valid: true,
        cleaned: {
            user_id: raw.user_id.trim(),
            session_id: raw.session_id.trim(),
            x: Math.round(raw.x),
            y: Math.round(raw.y),
            timestamp,
            page: raw.page || '/',
        },
    };
}

module.exports = { cleanEvent };
