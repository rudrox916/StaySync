from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from db import query_db, insert_db, update_db
from datetime import datetime, date
from functools import wraps
from types import SimpleNamespace

main_bp = Blueprint('main', __name__)


# ─── Wrappers for Template Compatibility ────────────────────────────
class BookingWrapper:
    def __init__(self, row):
        row = dict(row)
        self.id = row['id']
        self.user_id = row['user_id']
        self.room_id = row['room_id']
        self.total_price = row['total_price']
        self.status = row['status']
        
        # Parse dates into datetime objects for template formatting (.strftime)
        self.created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if isinstance(row['created_at'], str) else row['created_at']
        
        ci_str = row['check_in_date'].split()[0] if isinstance(row['check_in_date'], str) else row['check_in_date']
        co_str = row['check_out_date'].split()[0] if isinstance(row['check_out_date'], str) else row['check_out_date']
        self.check_in_date = datetime.strptime(ci_str, '%Y-%m-%d') if isinstance(ci_str, str) else ci_str
        self.check_out_date = datetime.strptime(co_str, '%Y-%m-%d') if isinstance(co_str, str) else co_str
        
        self.room = SimpleNamespace(
            room_number=row.get('room_number'),
            type=row.get('room_type'),
            hotel=SimpleNamespace(
                name=row.get('hotel_name'),
                location=row.get('hotel_location')
            )
        )
        self.user = SimpleNamespace(
            username=row.get('username')
        )

class RoomWrapper:
    def __init__(self, row):
        row = dict(row)
        self.id = row['id']
        self.hotel_id = row['hotel_id']
        self.room_number = row['room_number']
        self.type = row['type']
        self.price_per_night = row['price_per_night']
        self.capacity = row['capacity']
        self.is_available = row['is_available']
        self.hotel = SimpleNamespace(
            name=row.get('hotel_name'),
            location=row.get('hotel_location')
        )

class VenueWrapper:
    def __init__(self, row):
        row = dict(row)
        self.id = row['id']
        self.hotel_id = row['hotel_id']
        self.name = row['name']
        self.capacity = row['capacity']
        self.price_per_day = row['price_per_day']
        self.is_available = row['is_available']
        self.hotel = SimpleNamespace(
            name=row.get('hotel_name'),
            location=row.get('hotel_location')
        )


# ─── Admin Decorator ────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ─── Home ───────────────────────────────────────────────────────────
@main_bp.route('/')
def index():
    hotels = query_db("SELECT * FROM hotels LIMIT 6")
    return render_template('index.html', hotels=hotels)


# ─── Hotels ─────────────────────────────────────────────────────────
@main_bp.route('/hotels')
def hotels():
    q    = request.args.get('q', '').strip()
    sort = request.args.get('sort', '')
    
    if q:
        query_str = "SELECT * FROM hotels WHERE name LIKE ? OR location LIKE ?"
        params = (f'%{q}%', f'%{q}%')
    else:
        query_str = "SELECT * FROM hotels"
        params = ()
        
    if sort == 'rating':
        query_str += " ORDER BY rating DESC"
    elif sort == 'name':
        query_str += " ORDER BY name ASC"
        
    all_hotels = query_db(query_str, params)
    return render_template('hotels.html', hotels=all_hotels)


@main_bp.route('/hotels/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = query_db("SELECT * FROM hotels WHERE id = ?", (hotel_id,), one=True)
    if not hotel:
        abort(404)
    rooms = query_db("SELECT * FROM rooms WHERE hotel_id = ?", (hotel_id,))
    return render_template('hotel_detail.html', hotel=hotel, rooms=rooms)


# ─── Booking ────────────────────────────────────────────────────────
@main_bp.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    # Retrieve room with hotel details for summary
    row = query_db(
        "SELECT r.*, h.name as hotel_name, h.location as hotel_location "
        "FROM rooms r "
        "JOIN hotels h ON r.hotel_id = h.id "
        "WHERE r.id = ?", (room_id,), one=True
    )
    if not row:
        abort(404)
        
    room = RoomWrapper(row)

    if not room.is_available:
        flash('This room is currently not available.', 'warning')
        return redirect(url_for('main.hotel_detail', hotel_id=room.hotel_id))

    if request.method == 'POST':
        check_in_str  = request.form.get('check_in')
        check_out_str = request.form.get('check_out')

        try:
            check_in  = datetime.strptime(check_in_str,  '%Y-%m-%d')
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            flash('Invalid dates provided.', 'danger')
            return redirect(url_for('main.book_room', room_id=room_id))

        if check_out <= check_in:
            flash('Check-out must be after check-in.', 'danger')
            return redirect(url_for('main.book_room', room_id=room_id))

        nights      = (check_out - check_in).days
        total_price = nights * room.price_per_night

        # Insert booking with raw SQL
        insert_db(
            "INSERT INTO bookings (user_id, room_id, check_in_date, check_out_date, total_price, status) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user.id, room.id, check_in_str, check_out_str, total_price, 'pending')
        )

        flash(f'Booking confirmed for {nights} night(s)! Total: ₹{total_price:.0f}', 'success')
        return redirect(url_for('main.my_bookings'))

    return render_template('book_room.html', room=room, today=date.today().isoformat())


# ─── Events ─────────────────────────────────────────────────────────
@main_bp.route('/events')
def events():
    rows = query_db(
        "SELECT ev.*, h.name as hotel_name, h.location as hotel_location "
        "FROM event_venues ev "
        "JOIN hotels h ON ev.hotel_id = h.id"
    )
    venues = [VenueWrapper(r) for r in rows]
    return render_template('events.html', venues=venues)


# ─── Dashboard ──────────────────────────────────────────────────────
@main_bp.route('/dashboard')
@login_required
def dashboard():
    rows = query_db(
        "SELECT b.*, r.room_number, r.type as room_type, h.name as hotel_name, h.location as hotel_location "
        "FROM bookings b "
        "JOIN rooms r ON b.room_id = r.id "
        "JOIN hotels h ON r.hotel_id = h.id "
        "WHERE b.user_id = ? "
        "ORDER BY b.created_at DESC",
        (current_user.id,)
    )
    bookings = [BookingWrapper(r) for r in rows]
    total_spent = sum(b.total_price for b in bookings if b.status != 'cancelled')
    return render_template('dashboard.html', bookings=bookings, total_spent=total_spent)


@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    rows = query_db(
        "SELECT b.*, r.room_number, r.type as room_type, h.name as hotel_name, h.location as hotel_location "
        "FROM bookings b "
        "JOIN rooms r ON b.room_id = r.id "
        "JOIN hotels h ON r.hotel_id = h.id "
        "WHERE b.user_id = ? "
        "ORDER BY b.created_at DESC",
        (current_user.id,)
    )
    bookings = [BookingWrapper(r) for r in rows]
    return render_template('my_bookings.html', bookings=bookings)


@main_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = query_db("SELECT * FROM bookings WHERE id = ?", (booking_id,), one=True)
    if not booking:
        abort(404)
        
    if booking['user_id'] != current_user.id and current_user.role != 'admin':
        abort(403)
        
    update_db("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    flash('Booking cancelled successfully.', 'info')
    return redirect(url_for('main.my_bookings'))


# ─── Admin Panel ────────────────────────────────────────────────────
@main_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    stats = {
        'hotels':   query_db("SELECT COUNT(*) FROM hotels", one=True)[0],
        'rooms':    query_db("SELECT COUNT(*) FROM rooms", one=True)[0],
        'users':    query_db("SELECT COUNT(*) FROM users", one=True)[0],
        'bookings': query_db("SELECT COUNT(*) FROM bookings", one=True)[0],
    }
    
    rows = query_db(
        "SELECT b.*, u.username, r.room_number, r.type as room_type, h.name as hotel_name, h.location as hotel_location "
        "FROM bookings b "
        "JOIN users u ON b.user_id = u.id "
        "JOIN rooms r ON b.room_id = r.id "
        "JOIN hotels h ON r.hotel_id = h.id "
        "ORDER BY b.created_at DESC"
    )
    all_bookings = [BookingWrapper(r) for r in rows]
    hotels = query_db("SELECT * FROM hotels")
    
    return render_template('admin.html', stats=stats, all_bookings=all_bookings, hotels=hotels)


@main_bp.route('/admin/add-hotel', methods=['POST'])
@login_required
@admin_required
def add_hotel():
    name = request.form.get('name')
    location = request.form.get('location')
    description = request.form.get('description')
    rating = float(request.form.get('rating') or 0)
    image_url = request.form.get('image_url') or None
    amenities = request.form.get('amenities')

    insert_db(
        "INSERT INTO hotels (name, location, description, rating, image_url, amenities) VALUES (?, ?, ?, ?, ?, ?)",
        (name, location, description, rating, image_url, amenities)
    )
    
    flash(f'Hotel "{name}" added successfully!', 'success')
    return redirect(url_for('main.admin_panel'))


@main_bp.route('/admin/add-room', methods=['POST'])
@login_required
@admin_required
def add_room():
    hotel_id = int(request.form.get('hotel_id'))
    room_number = request.form.get('room_number')
    room_type = request.form.get('type')
    price = float(request.form.get('price'))
    capacity = int(request.form.get('capacity'))

    insert_db(
        "INSERT INTO rooms (hotel_id, room_number, type, price_per_night, capacity, is_available) VALUES (?, ?, ?, ?, ?, ?)",
        (hotel_id, room_number, room_type, price, capacity, 1)
    )
    
    flash(f'Room {room_number} added!', 'success')
    return redirect(url_for('main.admin_panel'))


@main_bp.route('/admin/confirm-booking/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def confirm_booking(booking_id):
    rowcount = update_db("UPDATE bookings SET status = 'confirmed' WHERE id = ?", (booking_id,))
    if rowcount == 0:
        abort(404)
        
    flash(f'Booking #{booking_id} confirmed.', 'success')
    return redirect(url_for('main.admin_panel'))


# ─── Error Handlers ─────────────────────────────────────────────────
@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
