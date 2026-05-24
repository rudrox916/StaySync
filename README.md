# StaySync 🏨

> **Smart Hotel & Event Resource Manager** – A full-stack web application built with Flask, SQLAlchemy, and Bootstrap 5.

---

## 📁 Project Structure

```
StaySync/
├── app.py               # Application factory (Flask)
├── config.py            # Configuration (DB URI, secret key)
├── extensions.py        # SQLAlchemy & LoginManager instances
├── seed.py              # Database seeder with sample data
├── requirements.txt     # Python dependencies
│
├── models/
│   └── __init__.py      # User, Hotel, Room, EventVenue, Booking models
│
├── routes/
│   ├── __init__.py
│   ├── main.py          # Home, hotels, bookings, admin routes
│   └── auth.py          # Login, register, logout
│
├── templates/
│   ├── base.html        # Base layout (navbar, flash msgs, footer)
│   ├── index.html       # Landing page
│   ├── hotels.html      # Hotels listing
│   ├── hotel_detail.html# Hotel + rooms detail
│   ├── book_room.html   # Room booking form
│   ├── dashboard.html   # User dashboard
│   ├── my_bookings.html # All user bookings
│   ├── events.html      # Event venues
│   ├── admin.html       # Admin panel
│   ├── login.html
│   ├── register.html
│   └── errors/
│       ├── 404.html
│       └── 403.html
│
└── static/
    └── style.css        # Dark glassmorphism theme
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd StaySync
pip install -r requirements.txt
```

### 2. Configure Database

**Option A – SQLite (default, no setup needed)**  
The app auto-creates `staysync.db` on first run.

**Option B – MySQL**  
```bash
export DATABASE_URL="mysql+pymysql://user:password@localhost/staysync"
```

### 3. Seed Sample Data

```bash
python seed.py
```

This creates:
- 5 hotels with rooms & venues across India  
- 4 users (admin, manager, alice, bob)  
- 3 sample bookings  

| Username | Password   | Role     |
|----------|-----------|----------|
| admin    | admin123  | admin    |
| manager  | manager123| manager  |
| alice    | alice123  | customer |
| bob      | bob123    | customer |

### 4. Run the App

```bash
python app.py
```

Visit → **http://localhost:5000**

---

## 🗃️ Database Schema

```
users          → id, username, email, password_hash, role, created_at
hotels         → id, name, description, location, amenities, rating, image_url
rooms          → id, hotel_id, room_number, type, price_per_night, capacity, is_available
event_venues   → id, hotel_id, name, capacity, price_per_day, is_available
bookings       → id, user_id, room_id, check_in_date, check_out_date, total_price, status, created_at
```

---

## ✨ Features (Phase 1 – DBMS)

- [x] User registration & login (Flask-Login)
- [x] Role-based access (customer / manager / admin)
- [x] Hotel & room management (admin CRUD)
- [x] Room booking with date selection & live price preview
- [x] Booking cancellation
- [x] Admin can confirm/cancel bookings
- [x] Event venue listing
- [x] User dashboard with booking stats
- [x] Hotel search & sort
- [x] Responsive dark glassmorphism UI

---

## 🔮 Upcoming Phases

| Phase | Focus |
|-------|-------|
| Phase 2 | Analytics dashboard (revenue, occupancy, events) |
| Phase 3 | AI/ML – demand prediction, dynamic pricing, recommendations |
| Phase 4 | REST API, email notifications, PDF invoices, deployment |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask 3 |
| ORM | SQLAlchemy |
| Auth | Flask-Login |
| Frontend | HTML5, Bootstrap 5, Vanilla JS |
| Styling | Custom CSS (glassmorphism) |
| Database | SQLite (dev) / MySQL (prod) |

---

*Built as a DBMS project with scalability toward Data Science integration.*
