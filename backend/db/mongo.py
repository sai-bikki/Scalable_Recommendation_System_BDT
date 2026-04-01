from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = None
db = None

def connect_mongo():
    global client, db
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/analytics')
    client = MongoClient(mongo_uri)
    db = client['analytics']
    print('✅ MongoDB connected')
    return db

def get_db():
    return db

def close_mongo():
    if client:
        client.close()
