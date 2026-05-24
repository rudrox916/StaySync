"""
analytics_service.py – Revenue and occupancy helpers.
Used by Phase 2 analytics dashboard.
"""

from models import Booking, Room, Hotel
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta


def revenue_last_n_days(n: int = 30) -> float:
    """Total revenue from confirmed bookings in the last N days."""
    since = datetime.utcnow() - timedelta(days=n)
    result = (
        db.session.query(func.sum(Booking.total_price))
        .filter(Booking.status == 'confirmed', Booking.created_at >= since)
        .scalar()
    )
    return float(result or 0)


def occupancy_rate(hotel_id: int = None) -> dict:
    """
    Returns dict with total_rooms and booked_rooms counts.
    Optionally filter by hotel_id.
    """
    q = Room.query
    if hotel_id:
        q = q.filter(Room.hotel_id == hotel_id)
    total  = q.count()
    booked = q.filter(Room.is_available == False).count()
    return {
        'total':  total,
        'booked': booked,
        'rate':   round((booked / total * 100), 1) if total else 0,
    }


def bookings_by_status() -> dict:
    """Counts of bookings grouped by status."""
    rows = (
        db.session.query(Booking.status, func.count(Booking.id))
        .group_by(Booking.status)
        .all()
    )
    return {status: count for status, count in rows}


def top_hotels_by_revenue(limit: int = 5) -> list:
    """Hotels ranked by total confirmed revenue."""
    rows = (
        db.session.query(Hotel.name, func.sum(Booking.total_price).label('revenue'))
        .join(Room,    Room.hotel_id  == Hotel.id)
        .join(Booking, Booking.room_id == Room.id)
        .filter(Booking.status == 'confirmed')
        .group_by(Hotel.id)
        .order_by(func.sum(Booking.total_price).desc())
        .limit(limit)
        .all()
    )
    return [{'hotel': r[0], 'revenue': float(r[1])} for r in rows]
