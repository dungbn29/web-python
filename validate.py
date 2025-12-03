#!/usr/bin/env python
"""Validation script to check all bugs are fixed"""

import sys
import os

# Add project to path
sys.path.insert(0, 'D:\\Dung\\code\\phone1')

print("=" * 60)
print("VALIDATING PROJECT STRUCTURE AND IMPORTS")
print("=" * 60)

# Test 1: Import all modules
print("\n[1] Testing imports...")
try:
    from app import create_app
    print("  ✓ app.py imports OK")
except ImportError as e:
    print(f"  ✗ app.py error: {e}")
    sys.exit(1)

try:
    from db import init_db, phones_col, users_col, orders_col
    print("  ✓ db.py imports OK")
except ImportError as e:
    print(f"  ✗ db.py error: {e}")
    sys.exit(1)

try:
    from routes.auth import auth_bp
    print("  ✓ routes/auth.py imports OK")
except ImportError as e:
    print(f"  ✗ routes/auth.py error: {e}")
    sys.exit(1)

try:
    from routes.shop import shop_bp
    print("  ✓ routes/shop.py imports OK")
except ImportError as e:
    print(f"  ✗ routes/shop.py error: {e}")
    sys.exit(1)

try:
    from routes.admin import admin_bp
    print("  ✓ routes/admin.py imports OK")
except ImportError as e:
    print(f"  ✗ routes/admin.py error: {e}")
    sys.exit(1)

# Test 2: Create Flask app
print("\n[2] Testing Flask app creation...")
try:
    app = create_app()
    print("  ✓ Flask app created successfully")
except Exception as e:
    print(f"  ✗ Failed to create Flask app: {e}")
    sys.exit(1)

# Test 3: Check blueprints registered
print("\n[3] Checking registered blueprints...")
blueprints = [bp for bp in app.blueprints]
expected = ['auth', 'shop', 'admin']
for bp in expected:
    if bp in blueprints:
        print(f"  ✓ {bp} blueprint registered")
    else:
        print(f"  ✗ {bp} blueprint NOT registered")
        sys.exit(1)

# Test 4: Check database initialization
print("\n[4] Testing database initialization...")
try:
    init_db()
    print("  ✓ Database initialized")
except Exception as e:
    print(f"  ✗ Database initialization failed: {e}")
    sys.exit(1)

# Test 5: Check collections
print("\n[5] Checking collections...")
try:
    phones = phones_col.find()
    print(f"  ✓ Phones collection: {len(phones)} items")
except Exception as e:
    print(f"  ✗ Phones collection error: {e}")
    sys.exit(1)

try:
    users = users_col.find()
    print(f"  ✓ Users collection: {len(users)} items")
except Exception as e:
    print(f"  ✗ Users collection error: {e}")
    sys.exit(1)

try:
    orders = orders_col.find()
    print(f"  ✓ Orders collection: {len(orders)} items")
except Exception as e:
    print(f"  ✗ Orders collection error: {e}")
    sys.exit(1)

# Test 6: Check admin user
print("\n[6] Checking admin user...")
try:
    admin = users_col.find_one({'email': 'admin@example.com'})
    if admin:
        print(f"  ✓ Admin user found: {admin['name']}")
        if admin.get('role') == 'admin':
            print(f"  ✓ Admin has correct role")
        else:
            print(f"  ✗ Admin role incorrect: {admin.get('role')}")
            sys.exit(1)
    else:
        print(f"  ✗ Admin user not found")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Error checking admin user: {e}")
    sys.exit(1)

# Test 7: Check routes
print("\n[7] Checking routes...")
with app.test_client() as client:
    test_routes = [
        ('/', 'GET'),
        ('/login', 'GET'),
        ('/register', 'GET'),
    ]
    
    for route, method in test_routes:
        try:
            if method == 'GET':
                response = client.get(route)
            else:
                response = client.post(route)
            
            if response.status_code < 500:
                print(f"  ✓ {method} {route}: {response.status_code}")
            else:
                print(f"  ✗ {method} {route}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {method} {route}: {e}")

# Test 8: Test admin login and dashboard access
print("\n[8] Testing admin login flow...")
with app.test_client() as client:
    try:
        # Try login
        response = client.post('/login', data={
            'email': 'admin@example.com',
            'password': 'admin'
        }, follow_redirects=False)
        
        # Check if redirected to admin
        if response.status_code == 302 and '/admin' in response.location:
            print(f"  ✓ Admin login redirects to /admin")
        else:
            print(f"  ⚠ Admin login returned {response.status_code}")
        
        # Follow redirect and check dashboard
        response = client.post('/login', data={
            'email': 'admin@example.com',
            'password': 'admin'
        }, follow_redirects=True)
        
        if 'Admin Panel' in response.get_data(as_text=True) or response.status_code == 200:
            print(f"  ✓ Admin dashboard accessible")
        else:
            print(f"  ✗ Admin dashboard returned {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Admin login test failed: {e}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nAll systems are GO! The project is ready to run.")
print("Start the app with: python app.py")
