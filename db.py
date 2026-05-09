import json
import os
#from datetime import datetime
import hashlib
from pymongo import MongoClient

# Kết nối tới MongoDB Localhost
client = MongoClient("mongodb://localhost:27017/")
db = client['phone_store_db'] # Tên Database

# Định nghĩa các Collections
phones_col = db['phones']
users_col = db['users']
orders_col = db['orders']

def load_phones_from_json():
    json_path = os.path.join(os.path.dirname(__file__), 'phones_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def init_db():
    # 1. Kiểm tra nếu chưa có dữ liệu điện thoại thì mới import từ JSON
    if phones_col.count_documents({}) == 0:
        phones_data = load_phones_from_json()
        if phones_data:
            phones_col.insert_many(phones_data)
            print(">>> Đã khởi tạo dữ liệu điện thoại từ JSON vào MongoDB.")

    # 2. Khởi tạo tài khoản Admin nếu chưa có
    admin_email = "admin@example.com"
    if users_col.find_one({"email": admin_email}) is None:
        admin_password = hashlib.sha256("admin".encode()).hexdigest()
        admin_user = {
            "email": admin_email,
            "password": admin_password,
            "name": "Admin",
            "role": "admin"
        }
        users_col.insert_one(admin_user)
        print(">>> Đã tạo tài khoản Admin mặc định trong MongoDB.")

    print(">>> Kết nối MongoDB thành công!")  