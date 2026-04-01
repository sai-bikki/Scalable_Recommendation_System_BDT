/**
 * tracker.js — Lightweight Analytics SDK
 * Include on any website with:
 *   <script src="http://localhost:3000/tracker.js"></script>
 *
 * This script runs automatically and:
 *  1. Generates a persistent user_id (localStorage) and session_id (sessionStorage)
 *  2. Calls POST /session/start on page load
 *  3. Captures all click events and sends them to POST /event
 */

(function () {
    'use strict';

    const API_BASE = 'http://localhost:3000';

    // ── Identity ────────────────────────────────────────────────────────────────

    function getOrCreate(storage, key) {
        let val = storage.getItem(key);
        if (!val) {
            // Simple UUID v4 generator (no dependencies)
            val = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                const r = (Math.random() * 16) | 0;
                const v = c === 'x' ? r : (r & 0x3) | 0x8;
                return v.toString(16);
            });
            storage.setItem(key, val);
        }
        return val;
    }

    const user_id = getOrCreate(localStorage, 'analytics_user_id');
    const session_id = getOrCreate(sessionStorage, 'analytics_session_id');

    // ── Send helper ─────────────────────────────────────────────────────────────

    function send(endpoint, data) {
        const url = API_BASE + endpoint;
        const payload = JSON.stringify(data);

        // Use sendBeacon when available (non-blocking, survives page unload)
        if (navigator.sendBeacon) {
            const blob = new Blob([payload], { type: 'application/json' });
            navigator.sendBeacon(url, blob);
        } else {
            // Fallback to fetch (fire-and-forget)
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: payload,
                keepalive: true,
            }).catch(function () { /* silently ignore errors */ });
        }
    }

    // ── Session Start ───────────────────────────────────────────────────────────

    function startSession() {
        fetch(API_BASE + '/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user_id, session_id: session_id }),
        }).catch(function () { /* silently ignore */ });
    }

    // ── Click Tracking ──────────────────────────────────────────────────────────

    function trackClick(event) {
        const data = {
            user_id: user_id,
            session_id: session_id,
            x: event.clientX,
            y: event.clientY,
            timestamp: new Date().toISOString(),
            page: window.location.pathname,
        };
        send('/event', data);
    }

    // ── Init ────────────────────────────────────────────────────────────────────

    function init() {
        startSession();
        document.addEventListener('click', trackClick, { passive: true });
        console.log(
            '[Analytics] Tracking initialized. user=' + user_id + ' session=' + session_id
        );
    }

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
