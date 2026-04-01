/**
 * seed.js — Demo data generator for the analytics tool
 *
 * Generates realistic demo data:
 *   • 10 unique users
 *   • 5 sessions per user  → 50 sessions total
 *   • 8-15 clicks per session → ~500 click events
 *   • Spread over the last 7 days
 *   • Coordinates match real elements on the demo site (nav, hero, products)
 *
 * Run from the backend folder:
 *   node seed.js
 */

require('dotenv').config();
const { v4: uuidv4 } = require('uuid');

const API = `http://localhost:${process.env.PORT || 3000}`;

// ── Realistic click zones on the demo site (1280×900 layout) ──────────────
// Each zone has a label, an x/y range, and a weight (probability)
const CLICK_ZONES = [
    // Nav bar links (y ≈ 39)
    { label: 'nav-home', x: [360, 430], y: [28, 52], weight: 8 },
    { label: 'nav-products', x: [435, 510], y: [28, 52], weight: 7 },
    { label: 'nav-deals', x: [512, 570], y: [28, 52], weight: 5 },
    { label: 'nav-about', x: [572, 630], y: [28, 52], weight: 3 },
    // Cart button
    { label: 'nav-cart', x: [900, 1050], y: [24, 56], weight: 6 },
    // Hero section
    { label: 'hero-cta', x: [370, 630], y: [380, 445], weight: 12 },
    // Product cards — Row 1 (y ≈ 700-940)
    { label: 'product-1', x: [40, 330], y: [670, 950], weight: 10 },
    { label: 'product-2', x: [350, 640], y: [670, 950], weight: 11 },
    { label: 'product-3', x: [660, 950], y: [670, 950], weight: 9 },
    { label: 'product-4', x: [970, 1260], y: [670, 950], weight: 7 },
    // Product cards — Row 2 (y ≈ 980-1220)
    { label: 'product-5', x: [40, 330], y: [980, 1240], weight: 6 },
    { label: 'product-6', x: [350, 640], y: [980, 1240], weight: 8 },
    { label: 'product-7', x: [660, 950], y: [980, 1240], weight: 5 },
    { label: 'product-8', x: [970, 1260], y: [980, 1240], weight: 4 },
    // Add to Cart buttons (within cards)
    { label: 'add-cart-1', x: [60, 310], y: [910, 945], weight: 14 },
    { label: 'add-cart-2', x: [370, 620], y: [910, 945], weight: 16 },
    { label: 'add-cart-3', x: [680, 930], y: [910, 945], weight: 13 },
    { label: 'add-cart-4', x: [990, 1240], y: [910, 945], weight: 9 },
];

const TOTAL_WEIGHT = CLICK_ZONES.reduce((s, z) => s + z.weight, 0);

function randomZone() {
    let r = Math.random() * TOTAL_WEIGHT;
    for (const z of CLICK_ZONES) {
        r -= z.weight;
        if (r <= 0) return z;
    }
    return CLICK_ZONES[0];
}

function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randBetween(arr) {
    return randInt(arr[0], arr[1]);
}

// ── HTTP helpers ──────────────────────────────────────────────────────────────
async function post(path, body) {
    const res = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return res.json();
}

// ── Seed ──────────────────────────────────────────────────────────────────────
const USERS = 10;
const SESSIONS_PER = 5;
const DAYS_BACK = 7;

async function seed() {
    console.log('🌱 Starting seed...\n');

    let totalSessions = 0;
    let totalClicks = 0;
    let errors = 0;

    const now = Date.now();

    for (let u = 0; u < USERS; u++) {
        const user_id = uuidv4();

        for (let s = 0; s < SESSIONS_PER; s++) {
            const session_id = uuidv4();

            // Spread sessions over the last 7 days
            // Earlier users/sessions are older
            const daysAgo = DAYS_BACK - ((u * SESSIONS_PER + s) / (USERS * SESSIONS_PER)) * DAYS_BACK;
            const sessionStart = now - daysAgo * 86400_000 - randInt(0, 3600_000);

            // 1. Register session (upsert user in MongoDB)
            try {
                await post('/session/start', { user_id, session_id });
            } catch (e) {
                console.error(`  ⚠ session/start failed: ${e.message}`);
                errors++;
            }

            // 2. Generate 8–15 clicks for this session
            const clickCount = randInt(8, 15);
            let t = sessionStart;

            for (let c = 0; c < clickCount; c++) {
                const zone = randomZone();
                const x = randBetween(zone.x);
                const y = randBetween(zone.y);

                // Time between clicks: 0.5s – 8s
                t += randInt(500, 8000);

                const payload = {
                    user_id,
                    session_id,
                    x,
                    y,
                    timestamp: new Date(t).toISOString(),
                    page: '/demo/',
                };

                try {
                    const result = await post('/event', payload);
                    if (result.status === 'ok') {
                        totalClicks++;
                    } else {
                        errors++;
                    }
                } catch (e) {
                    errors++;
                }
            }

            totalSessions++;
            process.stdout.write(
                `\r  ✅ Sessions: ${totalSessions}/${USERS * SESSIONS_PER}  Clicks: ${totalClicks}  Errors: ${errors}  `
            );

            // Small delay between sessions to avoid hammering the server
            await new Promise(r => setTimeout(r, 50));
        }
    }

    console.log(`\n\n🎉 Seed complete!`);
    console.log(`   Users:    ${USERS}`);
    console.log(`   Sessions: ${totalSessions}`);
    console.log(`   Clicks:   ${totalClicks}`);
    console.log(`   Errors:   ${errors}`);
    console.log(`\n📊 Open Grafana → http://localhost:3001`);
    console.log(`   Dashboard → Analytics Overview`);
    console.log(`   Set time range to "Last 7 days"`);
    console.log(`\n🎬 Copy any session_id from the list below and paste it into the dashboard:`);
}

seed().catch(console.error);
