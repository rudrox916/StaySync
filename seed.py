"""
seed.py  –  Populate the StaySync database with sample data using raw SQL.
Run once: python seed.py
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'staysync.db')

HOTELS = [
    {
        "name": "The Grand Palace",
        "location": "Mumbai, Maharashtra",
        "description": "An iconic luxury hotel in the heart of Mumbai, offering world-class amenities and stunning sea views.",
        "rating": 4.8,
        "amenities": "Pool, Spa, WiFi, Gym, Restaurant, Valet",
        "image_url": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
        "rooms": [
            {"room_number": "101", "type": "Single",  "price": 3500, "capacity": 1},
            {"room_number": "102", "type": "Double",  "price": 5500, "capacity": 2},
            {"room_number": "201", "type": "Suite",   "price": 12000,"capacity": 4},
            {"room_number": "202", "type": "Deluxe",  "price": 8000, "capacity": 3},
        ],
        "venues": [
            {"name": "Ballroom A", "capacity": 500, "price_per_day": 75000},
            {"name": "Conference Hall 1", "capacity": 100, "price_per_day": 20000},
        ],
    },
    {
        "name": "Blue Lagoon Resort",
        "location": "Goa",
        "description": "A beachside paradise with private cabanas, infinity pool, and breathtaking sunset views.",
        "rating": 4.6,
        "amenities": "Beach Access, Pool, WiFi, Water Sports, Bar",
        "image_url": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
        "rooms": [
            {"room_number": "G01", "type": "Single",  "price": 4000, "capacity": 1},
            {"room_number": "G02", "type": "Double",  "price": 6500, "capacity": 2},
            {"room_number": "G03", "type": "Suite",   "price": 15000,"capacity": 4},
        ],
        "venues": [
            {"name": "Beach Pavilion", "capacity": 200, "price_per_day": 35000},
        ],
    },
    {
        "name": "Royal Heritage Inn",
        "location": "Jaipur, Rajasthan",
        "description": "Step into royalty at our heritage property, blending Rajasthani architecture with modern luxuries.",
        "rating": 4.7,
        "amenities": "Heritage Tour, Camel Ride, Pool, Rooftop Restaurant, WiFi",
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80",
        "rooms": [
            {"room_number": "R01", "type": "Double",  "price": 5000, "capacity": 2},
            {"room_number": "R02", "type": "Suite",   "price": 18000,"capacity": 4},
            {"room_number": "R03", "type": "Deluxe",  "price": 9000, "capacity": 3},
        ],
        "venues": [
            {"name": "Durbar Hall", "capacity": 300, "price_per_day": 50000},
        ],
    },
    {
        "name": "Summit View Hotel",
        "location": "Shimla, Himachal Pradesh",
        "description": "Wake up to snow-capped mountains. A cozy mountain retreat with fireplace suites.",
        "rating": 4.5,
        "amenities": "Mountain View, Fireplace, WiFi, Café, Trekking Desk",
        "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
        "rooms": [
            {"room_number": "M01", "type": "Single",  "price": 2800, "capacity": 1},
            {"room_number": "M02", "type": "Double",  "price": 4500, "capacity": 2},
            {"room_number": "M03", "type": "Suite",   "price": 9500, "capacity": 3},
        ],
        "venues": [],
    },
    {
        "name": "Coastal Breeze Hotel",
        "location": "Chennai, Tamil Nadu",
        "description": "Modern business hotel with premium conference facilities, close to Marina Beach.",
        "rating": 4.3,
        "amenities": "Business Centre, Pool, WiFi, Restaurant, Airport Shuttle",
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80",
        "rooms": [
            {"room_number": "C01", "type": "Single",  "price": 3200, "capacity": 1},
            {"room_number": "C02", "type": "Double",  "price": 5000, "capacity": 2},
            {"room_number": "C03", "type": "Deluxe",  "price": 7500, "capacity": 3},
        ],
        "venues": [
            {"name": "Business Suite", "capacity": 80, "price_per_day": 15000},
        ],
    },
]

def seed():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Read and apply schema
    schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'schema.sql')
    print("Reading and applying database schema...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    conn.commit()

    # 2. Clear all tables
    print("Clearing existing data...")
    cursor.execute("DELETE FROM bookings;")
    cursor.execute("DELETE FROM event_venues;")
    cursor.execute("DELETE FROM rooms;")
    cursor.execute("DELETE FROM hotels;")
    cursor.execute("DELETE FROM users;")
    conn.commit()

    # 3. Seed users
    print("Seeding users...")
    users = [
        ('admin', 'admin@staysync.com', generate_password_hash('admin123'), 'admin'),
        ('manager', 'manager@staysync.com', generate_password_hash('manager123'), 'manager'),
        ('alice', 'alice@example.com', generate_password_hash('alice123'), 'customer'),
        ('bob', 'bob@example.com', generate_password_hash('bob123'), 'customer'),
    ]
    cursor.executemany(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        users
    )
    conn.commit()

    # Fetch user IDs
    cursor.execute("SELECT id, username FROM users")
    user_map = {row[1]: row[0] for row in cursor.fetchall()}

    # 4. Seed Hotels, Rooms, Venues
    print("Seeding hotels, rooms, and venues...")
    for h in HOTELS:
        cursor.execute(
            "INSERT INTO hotels (name, location, description, rating, amenities, image_url) VALUES (?, ?, ?, ?, ?, ?)",
            (h['name'], h['location'], h['description'], h['rating'], h['amenities'], h['image_url'])
        )
        hotel_id = cursor.lastrowid
        
        for r in h['rooms']:
            cursor.execute(
                "INSERT INTO rooms (hotel_id, room_number, type, price_per_night, capacity, is_available) VALUES (?, ?, ?, ?, ?, ?)",
                (hotel_id, r['room_number'], r['type'], r['price'], r['capacity'], 1)
            )
            
        for v in h.get('venues', []):
            cursor.execute(
                "INSERT INTO event_venues (hotel_id, name, capacity, price_per_day, is_available) VALUES (?, ?, ?, ?, ?)",
                (hotel_id, v['name'], v['capacity'], v['price_per_day'], 1)
            )
    conn.commit()

    # Fetch rooms
    cursor.execute("SELECT id FROM rooms")
    room_ids = [row[0] for row in cursor.fetchall()]

    # 5. Seed historical bookings for analytics trend mapping
    print("Seeding sample and historical bookings...")
    bookings = [
        (user_map['alice'], room_ids[0], '2025-12-20', '2025-12-23', 10500.0, 'confirmed', '2025-12-01 10:00:00'),
        (user_map['alice'], room_ids[2], '2026-01-05', '2026-01-08', 36000.0, 'pending',   '2026-01-02 12:00:00'),
        (user_map['bob'],   room_ids[4], '2026-02-14', '2026-02-17', 19500.0, 'confirmed', '2026-02-10 14:00:00'),
        
        # Historical records (Confirmed) for Monthly Revenue chart
        (user_map['alice'], room_ids[0], '2025-06-10', '2025-06-12', 7000.0,  'confirmed', '2025-06-08 09:30:00'),
        (user_map['bob'],   room_ids[1], '2025-07-15', '2025-07-18', 16500.0, 'confirmed', '2025-07-12 11:20:00'),
        (user_map['alice'], room_ids[3], '2025-08-20', '2025-08-22', 16000.0, 'confirmed', '2025-08-15 15:45:00'),
        (user_map['bob'],   room_ids[2], '2025-09-05', '2025-09-08', 36000.0, 'confirmed', '2025-09-01 10:00:00'),
        (user_map['alice'], room_ids[4], '2025-10-10', '2025-10-14', 26000.0, 'confirmed', '2025-10-05 14:15:00'),
        (user_map['bob'],   room_ids[0], '2025-11-12', '2025-11-15', 10500.0, 'confirmed', '2025-11-08 12:30:00'),
    ]
    cursor.executemany(
        "INSERT INTO bookings (user_id, room_id, check_in_date, check_out_date, total_price, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        bookings
    )
    conn.commit()
    conn.close()

    print("\n✅ Database seeded successfully using raw SQL!")
    print("   Admin   →  admin / admin123")
    print("   User    →  alice / alice123")

if __name__ == '__main__':
    seed()
