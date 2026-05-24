from flask import Blueprint, render_template, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from db import query_db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ─── Main Analytics Page ─────────────────────────────────────────────
@analytics_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('analytics.html')


# ─── API: Revenue by month (last 12 months) ──────────────────────────
@analytics_bp.route('/api/revenue')
@login_required
@admin_required
def api_revenue():
    twelve_months_ago = (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    
    rows = query_db(
        "SELECT strftime('%Y', created_at) as yr, strftime('%m', created_at) as mo, SUM(total_price) as revenue "
        "FROM bookings "
        "WHERE status = 'confirmed' AND created_at >= ? "
        "GROUP BY yr, mo "
        "ORDER BY yr, mo",
        (twelve_months_ago,)
    )
    
    labels, data = [], []
    for row in rows:
        month_name = datetime(int(row['yr']), int(row['mo']), 1).strftime('%b %Y')
        labels.append(month_name)
        data.append(float(row['revenue'] or 0))
    return jsonify({'labels': labels, 'data': data})


# ─── API: Bookings by status ──────────────────────────────────────────
@analytics_bp.route('/api/bookings-status')
@login_required
@admin_required
def api_bookings_status():
    rows = query_db(
        "SELECT status, COUNT(id) as count "
        "FROM bookings "
        "GROUP BY status"
    )
    labels = [row['status'].capitalize() for row in rows]
    data   = [row['count'] for row in rows]
    return jsonify({'labels': labels, 'data': data})


# ─── API: Occupancy per hotel ─────────────────────────────────────────
@analytics_bp.route('/api/occupancy')
@login_required
@admin_required
def api_occupancy():
    hotels = query_db("SELECT * FROM hotels")
    labels, booked, available = [], [], []
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    for h in hotels:
        total = query_db("SELECT COUNT(*) FROM rooms WHERE hotel_id = ?", (h['id'],), one=True)[0]
        
        busy = query_db(
            "SELECT COUNT(b.id) "
            "FROM bookings b "
            "JOIN rooms r ON r.id = b.room_id "
            "WHERE r.hotel_id = ? "
            "AND b.status IN ('pending', 'confirmed') "
            "AND b.check_out_date >= ?",
            (h['id'], now_str), one=True
        )[0] or 0
        
        labels.append(h['name'])
        booked.append(min(busy, total))
        available.append(max(total - busy, 0))
        
    return jsonify({'labels': labels, 'booked': booked, 'available': available})


# ─── API: Top hotels by revenue ───────────────────────────────────────
@analytics_bp.route('/api/top-hotels')
@login_required
@admin_required
def api_top_hotels():
    rows = query_db(
        "SELECT h.name, SUM(b.total_price) as rev "
        "FROM bookings b "
        "JOIN rooms r ON b.room_id = r.id "
        "JOIN hotels h ON r.hotel_id = h.id "
        "WHERE b.status = 'confirmed' "
        "GROUP BY h.id, h.name "
        "ORDER BY rev DESC "
        "LIMIT 5"
    )
    labels = [r['name'] for r in rows]
    data   = [float(r['rev'] or 0) for r in rows]
    return jsonify({'labels': labels, 'data': data})


# ─── API: Summary KPIs ────────────────────────────────────────────────
@analytics_bp.route('/api/kpis')
@login_required
@admin_required
def api_kpis():
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    total_revenue = query_db(
        "SELECT SUM(total_price) FROM bookings WHERE status = 'confirmed'",
        one=True
    )[0] or 0

    this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
    monthly_revenue = query_db(
        "SELECT SUM(total_price) FROM bookings WHERE status = 'confirmed' AND created_at >= ?",
        (this_month_start,), one=True
    )[0] or 0

    total_rooms = query_db("SELECT COUNT(*) FROM rooms", one=True)[0] or 0
    
    active_rooms = query_db(
        "SELECT COUNT(DISTINCT room_id) "
        "FROM bookings "
        "WHERE status IN ('pending', 'confirmed') "
        "AND check_out_date >= ?",
        (now_str,), one=True
    )[0] or 0

    total_bookings = query_db("SELECT COUNT(*) FROM bookings", one=True)[0] or 0
    total_users = query_db("SELECT COUNT(*) FROM users", one=True)[0] or 0
    total_hotels = query_db("SELECT COUNT(*) FROM hotels", one=True)[0] or 0

    return jsonify({
        'total_revenue':   float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
        'total_bookings':  total_bookings,
        'total_users':     total_users,
        'total_hotels':    total_hotels,
        'total_rooms':     total_rooms,
        'active_bookings': active_rooms,
        'occupancy_rate':  round(active_rooms / total_rooms * 100, 1) if total_rooms else 0,
    })
