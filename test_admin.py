"""Test script to verify admin functionality"""
import sys
sys.path.insert(0, '/home/workspace')

from app import create_app
from db import init_db, phones_col, users_col, orders_col

# Initialize
app = create_app()

# Test admin login
print("Testing admin login...")
with app.test_client() as client:
    with client.session_transaction() as sess:
        pass  # Initialize session
    
    # Test login with admin credentials
    response = client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'admin'
    }, follow_redirects=True)
    
    print(f"Login response status: {response.status_code}")
    
    # Check if redirected to admin
    if response.status_code == 200:
        print("✓ Admin login successful")
        
        # Test admin dashboard
        response = client.get('/admin/')
        print(f"Admin dashboard status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Admin dashboard accessible")
        else:
            print("✗ Admin dashboard not accessible")
    else:
        print("✗ Admin login failed")

# Test database
print("\nTesting database...")
print(f"Number of phones: {len(phones_col.find())}")
print(f"Number of users: {len(users_col.find())}")
print(f"Number of orders: {len(orders_col.find())}")

# Test admin user
admin_user = users_col.find_one({'email': 'admin@example.com'})
if admin_user:
    print(f"✓ Admin user found: {admin_user['name']}")
else:
    print("✗ Admin user not found")

print("\nAll tests completed!")
