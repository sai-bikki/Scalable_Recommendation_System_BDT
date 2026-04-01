require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');

const connectMongo = require('./db/mongo');
const { connectInflux } = require('./db/influx');
const sessionRouter = require('./routes/session');
const eventsRouter = require('./routes/events');

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ────────────────────────────────────────────────────────────────
// Allow all origins including 'null' (file:// pages open with null origin)
app.use(cors({
    origin: (origin, callback) => callback(null, true),
    credentials: true,
}));
app.use(express.json());

// ── Static files ─────────────────────────────────────────────────────────────
app.use(express.static(path.join(__dirname, 'public')));         // tracker.js
app.use('/demo', express.static(path.join(__dirname, '..', 'demo-site')));  // → /demo
app.use('/dashboard', express.static(path.join(__dirname, '..', 'dashboard'))); // → /dashboard

// ── Routes ────────────────────────────────────────────────────────────────────
app.use('/session', sessionRouter);
app.use('/event', eventsRouter);

// ── Health check ──────────────────────────────────────────────────────────────
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// ── Start ─────────────────────────────────────────────────────────────────────
async function start() {
    try {
        await connectMongo();
        connectInflux();
        app.listen(PORT, () => {
            console.log(`🚀 Analytics backend running at http://localhost:${PORT}`);
            console.log(`   tracker.js  → http://localhost:${PORT}/tracker.js`);
            console.log(`   demo site   → http://localhost:${PORT}/demo`);
            console.log(`   dashboard   → http://localhost:${PORT}/dashboard`);
        });
    } catch (err) {
        console.error('Failed to start server:', err);
        process.exit(1);
    }
}

start();
