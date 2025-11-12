from pymongo import MongoClient
from datetime import datetime
from loguru import logger
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://root:root@localhost:27017/?authSource=admin")
DB_NAME = os.getenv("MONGODB_DB", "depression_social_media")  
# To manage the MongoDB connection
def connecter_mongodb(MONGODB_URI,DB_NAME):
    # Create a connection to the MongoDB server
    try:
        client = MongoClient(MONGODB_URI)
        dblist = client.list_database_names()
        if DB_NAME in dblist:
            logger.info(f"Successfully connected to database {DB_NAME}")
            return client[DB_NAME]
        else:
            logger.info(f"Successfully connected to database {DB_NAME}")
            return client[DB_NAME]
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return None
def gerer_collections(db):
    # Create collections if they don't exist
    try:
        collections = db.list_collection_names()
        if "post_X" not in collections:
            db.create_collection("post_X")
        if "post_facebook" not in collections:
            db.create_collection("post_facebook")
    except Exception as e:
        logger.error(f"Error managing collections: {str(e)}")
        return None
    return db
    
