"""
booking_service.py – Business logic for booking operations.
Phase 1 DBMS layer; will be extended in later phases.
"""

from models import Booking, Room
from extensions import db
from datetime import datetime


def get_available_rooms(hotel_id: int, check_in: datetime, check_out: datetime):
    """
    Return rooms that have no confirmed/pending booking
    overlapping the requested dates.
    """
    busy_room_ids = (
        db.session.query(Booking.room_id)
        .filter(
            Booking.status.in_(['pending', 'confirmed']),
            Booking.check_in_date  < check_out,
            Booking.check_out_date > check_in,
        )
        .subquery()
    )
    return (
        Room.query
        .filter(Room.hotel_id == hotel_id)
        .filter(Room.id.notin_(busy_room_ids))
        .all()
    )


def create_booking(user_id: int, room_id: int,
                   check_in: datetime, check_out: datetime) -> Booking:
    """Create and persist a new booking; returns the Booking object."""
    room   = Room.query.get_or_404(room_id)
    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValueError("Check-out must be after check-in.")

    booking = Booking(
        user_id        = user_id,
        room_id        = room_id,
        check_in_date  = check_in,
        check_out_date = check_out,
        total_price    = nights * room.price_per_night,
        status         = 'pending',
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def cancel_booking(booking_id: int, requesting_user_id: int, is_admin: bool = False):
    """Cancel a booking if the user owns it or is admin."""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != requesting_user_id and not is_admin:
        raise PermissionError("Not authorised to cancel this booking.")
    booking.status = 'cancelled'
    db.session.commit()
    return booking
