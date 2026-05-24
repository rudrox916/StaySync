-- ============================================================
-- StaySync – SQLite Database Schema (DBMS Project)
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── Users Table ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'customer' CHECK(role IN ('customer', 'manager', 'admin')),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ── Hotels Table ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hotels (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    location    TEXT NOT NULL,
    amenities   TEXT,
    rating      REAL DEFAULT 0.0,
    image_url   TEXT
);

CREATE INDEX IF NOT EXISTS idx_hotels_location ON hotels(location);

-- ── Rooms Table ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rooms (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id        INTEGER NOT NULL,
    room_number     TEXT NOT NULL,
    type            TEXT NOT NULL CHECK(type IN ('Single', 'Double', 'Suite', 'Deluxe')),
    price_per_night REAL NOT NULL,
    capacity        INTEGER NOT NULL DEFAULT 2,
    is_available    BOOLEAN DEFAULT 1,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rooms_hotel ON rooms(hotel_id);
CREATE INDEX IF NOT EXISTS idx_rooms_available ON rooms(is_available);

-- ── Event Venues Table ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS event_venues (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id      INTEGER NOT NULL,
    name          TEXT NOT NULL,
    capacity      INTEGER NOT NULL,
    price_per_day REAL NOT NULL,
    is_available  BOOLEAN DEFAULT 1,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_venues_hotel ON event_venues(hotel_id);

-- ── Bookings Table ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    room_id        INTEGER NOT NULL,
    check_in_date  TEXT NOT NULL,
    check_out_date TEXT NOT NULL,
    total_price    REAL NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'cancelled')),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_room ON bookings(room_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);

-- ── Views for Analytics & Reports ────────────────────────────

-- Revenue summary per hotel
DROP VIEW IF EXISTS hotel_revenue;
CREATE VIEW hotel_revenue AS
    SELECT h.id, h.name, h.location,
           COUNT(b.id)         AS total_bookings,
           SUM(CASE WHEN b.status = 'confirmed' THEN b.total_price ELSE 0 END) AS total_revenue
    FROM   hotels h
    LEFT JOIN rooms   r ON r.hotel_id = h.id
    LEFT JOIN bookings b ON b.room_id  = r.id AND b.status = 'confirmed'
    GROUP BY h.id, h.name, h.location;

-- Occupancy overview
DROP VIEW IF EXISTS room_occupancy;
CREATE VIEW room_occupancy AS
    SELECT h.name AS hotel_name,
           r.room_number, r.type, r.price_per_night,
           r.is_available,
           COUNT(b.id)         AS booking_count
    FROM   rooms r
    JOIN   hotels  h ON h.id = r.hotel_id
    LEFT JOIN bookings b ON b.room_id = r.id AND b.status != 'cancelled'
    GROUP BY r.id, h.name;
