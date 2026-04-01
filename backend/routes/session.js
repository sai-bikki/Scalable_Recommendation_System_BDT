const express = require('express');
const router = express.Router();
const User = require('../models/User');

// POST /session/start
// Called by tracker.js on page load. Creates or updates user in MongoDB.
router.post('/start', async (req, res) => {
    const { user_id, session_id } = req.body;

    if (!user_id || !session_id) {
        return res.status(400).json({ error: 'user_id and session_id are required' });
    }

    try {
        const user = await User.findOneAndUpdate(
            { user_id },
            {
                last_seen: new Date(),
                $inc: { visit_count: 1 },
                $setOnInsert: { first_seen: new Date() },
            },
            { upsert: true, new: true }
        );

        console.log(`[session/start] user=${user_id} session=${session_id} visits=${user.visit_count}`);
        res.json({ status: 'ok', user_id, session_id, visit_count: user.visit_count });
    } catch (err) {
        console.error('[session/start] error:', err.message);
        res.status(500).json({ error: 'Failed to start session' });
    }
});

module.exports = router;
