const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    user_id: { type: String, required: true, unique: true },
    first_seen: { type: Date, default: Date.now },
    last_seen: { type: Date, default: Date.now },
    visit_count: { type: Number, default: 1 },
});

module.exports = mongoose.model('User', UserSchema);
