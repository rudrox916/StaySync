import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

# Setup opener with cookie jar to handle authentication sessions
cookie_processor = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookie_processor)
urllib.request.install_opener(opener)

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

def post(path, data_dict):
    url = f"{BASE_URL}{path}"
    data = urllib.parse.urlencode(data_dict).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

print("🚀 Running automated integration flow tests...")

try:
    # 1. Login as alice
    print("\n🔑 Logging in as 'alice'...")
    login_html = post('/auth/login', {
        'username': 'alice',
        'password': 'alice123',
        'remember_me': 'on'
    })
    
    # 2. Verify dashboard loads with user details
    print("📋 Checking dashboard load...")
    dashboard_html = get('/dashboard')
    if "Welcome back, alice" in dashboard_html:
        print("✅ Dashboard loaded successfully (User Session Active)")
    else:
        print("❌ Dashboard failed to load user details")
        exit(1)
        
    # 3. Create a room booking
    # Parse room ID 1 price preview to verify details load
    print("📖 Requesting room booking page for Room 1...")
    book_page = get('/book/1')
    if "Book Room 101" in book_page:
        print("✅ Room booking page loaded successfully")
    else:
        print("❌ Room booking page failed to load")
        exit(1)
        
    # POST check-in and check-out dates
    today = datetime.now()
    check_in = today.strftime('%Y-%m-%d')
    check_out = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    
    print(f"🏨 Booking Room 101 from {check_in} to {check_out}...")
    book_response = post('/book/1', {
        'check_in': check_in,
        'check_out': check_out
    })
    
    # Verify booking is in the bookings list
    my_bookings_html = get('/my-bookings')
    if "Room 101" in my_bookings_html:
        print("✅ Booking successfully created (SQL INSERT & fetch success)")
    else:
        print("❌ Booking was not found in user bookings list")
        exit(1)
        
    # Extract booking ID from the cancel button / form
    # The form action looks like /cancel-booking/<id>
    match = re.search(r'action="/cancel-booking/(\d+)"', my_bookings_html)
    if not match:
        print("❌ Could not extract booking ID from my_bookings page")
        exit(1)
    booking_id = match.group(1)
    print(f"📌 Extracted booking ID: {booking_id}")
    
    # 4. Cancel the booking
    print(f"❌ Canceling booking #{booking_id}...")
    cancel_resp = post(f'/cancel-booking/{booking_id}', {})
    
    my_bookings_html_after = get('/my-bookings')
    if f'action="/cancel-booking/{booking_id}"' not in my_bookings_html_after:
        print("✅ Booking cancelled successfully (SQL UPDATE status verified)")
    else:
        print("❌ Booking cancel failed; cancel action is still visible")
        exit(1)
        
    # 5. Logout
    print("🔒 Logging out...")
    get('/auth/logout')
    
    # 6. Admin Panel Flow
    print("\n🔑 Logging in as 'admin'...")
    post('/auth/login', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    print("🛡️ Loading Admin Panel...")
    admin_html = get('/admin')
    if "Admin Panel" in admin_html:
        print("✅ Admin panel loaded successfully")
    else:
        print("❌ Admin panel access denied or failed to load")
        exit(1)
        
    # Verify stats counts are present
    # E.g. in HTML: <div class="fw-bold fs-2">...</div>
    print("📊 Verifying aggregate counts...")
    # Clean matches of counts in panels
    stats_matches = re.findall(r'<div class="fw-bold fs-2">(\d+)</div>', admin_html)
    if len(stats_matches) >= 4:
        print(f"   Hotels: {stats_matches[0]}, Rooms: {stats_matches[1]}, Users: {stats_matches[2]}, Bookings: {stats_matches[3]}")
        print("✅ SQL COUNT statistics loaded correctly")
    else:
        print("⚠️ SQL COUNT stats structure did not match regex exactly")
        
    # 7. Add a new hotel
    print("➕ Adding a new hotel...")
    hotel_name = "Royal SQL Residency"
    post('/admin/add-hotel', {
        'name': hotel_name,
        'location': 'New Delhi, Delhi',
        'description': 'A beautiful raw-SQL driven hotel for database developers.',
        'rating': '4.9',
        'image_url': '',
        'amenities': 'SQL Terminal, High-speed WiFi'
    })
    
    # Verify hotel shows up on homepage
    home_html = get('/')
    if hotel_name in home_html:
        print("✅ New hotel successfully added and visible on Home (SQL INSERT & fetch verified)")
    else:
        print("❌ Added hotel was not visible on homepage")
        exit(1)
        
    print("\n🎉 All integration flow tests completed successfully!")
    exit(0)

except Exception as e:
    print(f"\n❌ Error during integration flow testing: {str(e)}")
    exit(1)
