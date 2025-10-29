# chat/mongo_client.py
from pymongo import MongoClient
from django.conf import settings

def get_db_handle():
    """
    Handles the connection to the MongoDB database.
    """
    try:
        client = MongoClient(settings.MONGO_DB_URL)
        # It's good practice to specify the database name
        db = client['rent_db'] 
        return db, client
    except Exception as e:
        # Handle connection errors gracefully
        print(f"Error connecting to MongoDB: {e}")
        return None, None