from pymongo import MongoClient

client = None
phones_col = None
users_col = None

def init_db():
    global client, phones_col, users_col
    client = MongoClient("mongodb://localhost:27017")  
    db = client["phone_shop"]
    phones_col = db["phones"]
    users_col = db["user"]