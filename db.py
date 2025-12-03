import json
import os
from datetime import datetime
import hashlib

# Load data from JSON file
def load_phones_data():
    json_path = os.path.join(os.path.dirname(__file__), 'phones_data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# In-memory storage
phones_data = []
users_data = []
orders_data = []

class PhonesCollection:
    def __init__(self, data):
        self.data = data
    
    def find(self, query=None):
        if query is None:
            return self.data
        result = []
        for item in self.data:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                result.append(item)
        return result
    
    def find_one(self, query):
        for item in self.data:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                return item
        return None
    
    def update_one(self, query, update):
        item = self.find_one(query)
        if item:
            if "$inc" in update:
                for key, value in update["$inc"].items():
                    if key in item:
                        item[key] += value
            elif "$set" in update:
                for key, value in update["$set"].items():
                    item[key] = value
    
    def insert_one(self, document):
        document['_id'] = str(datetime.utcnow().timestamp())
        self.data.append(document)
        return document
    
    def delete_one(self, query):
        item = self.find_one(query)
        if item:
            self.data.remove(item)
            return True
        return False
    
    def sort(self, field, direction):
        return sorted(self.data, key=lambda x: x.get(field, ''), reverse=(direction == -1))
    
    @property
    def database(self):
        return MockDatabase()

class MockDatabase:
    def __init__(self):
        global orders_col
        self.orders = orders_col if orders_col else OrdersCollection([])
    
    def __getattr__(self, name):
        global orders_col
        if name == 'orders':
            return orders_col if orders_col else OrdersCollection([])
        return OrdersCollection([])

class OrdersCollection:
    def __init__(self, data):
        self.data = data
    
    def find(self, query=None):
        if query is None:
            return self.data
        result = []
        for item in self.data:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                result.append(item)
        return result
    
    def find_one(self, query):
        for item in self.data:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                return item
        return None
    
    def insert_one(self, document):
        document['_id'] = str(datetime.utcnow().timestamp())
        self.data.append(document)
        return document
    
    def sort(self, field, direction):
        return sorted(self.data, key=lambda x: x.get(field, ''), reverse=(direction == -1))

phones_col = None
users_col = None
orders_col = None

def init_db():
    global phones_col, users_col, orders_col, users_data, orders_data
    phones_data = load_phones_data()
    phones_col = PhonesCollection(phones_data)
    
    # Initialize admin user
    admin_password = hashlib.sha256("admin".encode()).hexdigest()
    users_data = [
        {"email": "admin@example.com", "password": admin_password, "name": "Admin", "role": "admin"}
    ]
    users_col = PhonesCollection(users_data)
    
    # Initialize orders collection
    orders_col = OrdersCollection(orders_data)
    
    # Set up database reference for phones_col
    phones_col._db = MockDatabase()  