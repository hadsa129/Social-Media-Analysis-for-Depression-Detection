from pymongo import MongoClient
from datetime import datetime
import os
import re
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from loguru import logger

# Configuration MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://root:root@localhost:27017/?authSource=admin")
DB_NAME = os.getenv("MONGODB_DB", "depression_social_media")

def connecter_mongodb(MONGODB_URI, DB_NAME):
    # Connect to MongoDB
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
    """Create collections if they don't exist"""
    try:
        collections = db.list_collection_names()

        if "post_transformed_facebook" not in collections:
            db.create_collection("post_transformed_facebook")
        if "post_predicted_facebook" not in collections:
            db.create_collection("post_predicted_facebook")
      
        if "post_transformed_twitter" not in collections:
            db.create_collection("post_transformed_twitter")
        if "post_predicted_twitter" not in collections:
            db.create_collection("post_predicted_twitter")
    except Exception as e:
        logger.error(f"Error managing collections: {str(e)}")
        return None
    return db

def nettoyage(post):
    """Clean the text"""
    post = post.lower()
    post = post.strip()
    post = re.sub(r"\s+", " ", post)
    # Supprimer les URLs
    post = re.sub(r"http\S+|www\S+|https\S+", '', post)
    # Supprimer les mentions
    post = re.sub(r"@\S+", '', post)
    # Remove emojis
    post = emoji.replace_emoji(post, replace='')
    return post

def normaliser_text(post):
    """Normalize text using NLTK"""
    if not post:
        return ""
    
    post = post.lower()
    # Tokenize with nltk
    tokens = word_tokenize(post)
    stop_words = set(stopwords.words(['french', 'english']))
    # Filter stop words
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # Rebuild the text
    normalized_text = ' '.join(filtered_tokens)
    
    return normalized_text

def charger_transformed_facebook(db, original_text, transformed_text):
    """Load transformed Facebook text"""
    transformed = {
        "original_text": original_text,
        "transformed_text": transformed_text,
        "platform": "facebook",
        "processed_at": datetime.now().isoformat()
    }
    db.post_transformed_facebook.insert_one(transformed)

def charger_transformed_twitter(db, original_text, transformed_text):
    """Load transformed Twitter text"""
    transformed = {
        "original_text": original_text,
        "transformed_text": transformed_text,
        "platform": "twitter",
        "processed_at": datetime.now().isoformat()
    }
    db.post_transformed_twitter.insert_one(transformed)

def charger_prediction_facebook(db, text, theme, sentiment):
    """Load Facebook predictions"""
    prediction = {
        "text": text,
        "theme": theme.get("predicted_theme"),
        "sentiment": sentiment.get('label'),
        "platform": "facebook",
        "predicted_at": datetime.now().isoformat()
    }
    db.post_predicted_facebook.insert_one(prediction)

def charger_prediction_twitter(db, text, theme, sentiment):
    """Load Twitter predictions"""
    prediction = {
        "text": text,
        "theme": theme,
        "sentiment": sentiment,
        "platform": "twitter", 
        "predicted_at": datetime.now().isoformat()
    }
    db.post_predicted_twitter.insert_one(prediction)