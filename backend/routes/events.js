const express = require('express');
const router = express.Router();
const { getWriteApi, getQueryApi, Point } = require('../db/influx');
const { cleanEvent } = require('../cleaning/cleaner');

// POST /event
// Receives a click event from tracker.js, cleans it, and writes to InfluxDB.
router.post('/', async (req, res) => {
    const result = cleanEvent(req.body);

    if (!result.valid) {
        console.warn('[event] rejected:', result.errors);
        return res.status(400).json({ error: result.errors });
    }

    const { user_id, session_id, x, y, timestamp, page } = result.cleaned;

    try {
        const writeApi = getWriteApi();
        const point = new Point('clicks')
            .tag('user_id', user_id)
            .tag('session_id', session_id)
            .tag('page', page)
            .floatField('x', x)
            .floatField('y', y)
            .timestamp(timestamp);

        writeApi.writePoint(point);
        await writeApi.flush();

        console.log(`[event] click recorded x=${x} y=${y} user=${user_id}`);
        res.json({ status: 'ok' });
    } catch (err) {
        console.error('[event] influx write error:', err.message);
        res.status(500).json({ error: 'Failed to write event' });
    }
});

// GET /events?sessionId=xxx&limit=500
// Fetches click events for a given session from InfluxDB.
router.get('/', async (req, res) => {
    const { sessionId, limit = 500 } = req.query;

    if (!sessionId) {
        return res.status(400).json({ error: 'sessionId query param is required' });
    }

    const fluxQuery = `
    from(bucket: "${process.env.INFLUX_BUCKET}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "clicks")
      |> filter(fn: (r) => r.session_id == "${sessionId}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
      |> limit(n: ${parseInt(limit)})
  `;

    try {
        const queryApi = getQueryApi();
        const rows = [];

        await new Promise((resolve, reject) => {
            queryApi.queryRows(fluxQuery, {
                next(row, tableMeta) {
                    const obj = tableMeta.toObject(row);
                    rows.push({
                        timestamp: obj._time,
                        x: obj.x,
                        y: obj.y,
                        session_id: obj.session_id,
                        user_id: obj.user_id,
                        page: obj.page,
                    });
                },
                error: reject,
                complete: resolve,
            });
        });

        res.json({ session_id: sessionId, count: rows.length, events: rows });
    } catch (err) {
        console.error('[events] query error:', err.message);
        res.status(500).json({ error: 'Failed to query events' });
    }
});

module.exports = router;
