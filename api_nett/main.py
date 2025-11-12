from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import nltk 
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import your modules
from api_nett.ml import *
from api_nett.functions import *

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://root:root@localhost:27017/?authSource=admin")
DB_NAME = os.getenv("MONGODB_DB", "depression_social_media")

logger.info(f"Configuration - MONGODB_URI: {MONGODB_URI}")
logger.info(f"Configuration - DB_NAME: {DB_NAME}")

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Initialize FastAPI application
app = FastAPI(
    title="API ",
    version="1.0.0"
)



# Initialization
db = connecter_mongodb(MONGODB_URI, DB_NAME)
db = gerer_collections(db)
load_models()

@app.get("/")
def root():
    return {"message": "API "}




@app.post("/transform_facebook")
def transform_facebook():
    """Transform all raw Facebook posts"""
    try:
        print("Starting transformation of Facebook posts...")
        db = connecter_mongodb(MONGODB_URI, DB_NAME)
        if db is None:
            return {
                "status": "error",
                "message": "Impossible to connect to the database",
                "posts_transformes": 0,
                "platform": "facebook"
            }
            
        print("Retrieving raw Facebook posts...")
        post_brut_facebook = db.get_collection("post_brut_facebook")
        if post_brut_facebook is None:
            return {
                "status": "error",
                "message": "The 'post_brut_facebook' collection does not exist",
                "posts_transformes": 0,
                "platform": "facebook"
            }
            
        facebook_posts = list(post_brut_facebook.find({}))
        print(f"{len(facebook_posts)} posts to process")
        
        transformed_count = 0
        for i, post in enumerate(facebook_posts, 1):
            try:
                content = post.get('content', '')
                if not content:
                    logger.debug(f"Post {i}: No content to process")
                    continue
                    
                try:
                    logger.debug(f"Processing post {i}/{len(facebook_posts)}")
                    
                    # Clean the text
                    cleaned_text = nettoyage(content)
                    logger.debug("Text cleaned successfully")
                    
                    # Normalize the text
                    normalized_text = normaliser_text(cleaned_text)
                    logger.debug("Text normalized successfully")
                    
                    # Save the transformed text
                    logger.debug("Saving the transformed post...")
                    charger_transformed_facebook(db, content, normalized_text)
                    
                        
                    transformed_count += 1
                    logger.info(f"Post {i} transformed and saved")
                    
                except Exception as e:
                    logger.error(f"Error processing post {i}: {str(e)}", exc_info=True)
                    continue
                    
            except Exception as e:
                logger.error(f"Error processing post {i}: {str(e)}", exc_info=True)
                continue
        
        success_msg = f"Transformation complete. {transformed_count} posts transformed out of {len(facebook_posts)}."
        logger.info(success_msg)
        return {
            "status": "success",
            "message": success_msg,
            "posts_transformes": transformed_count,
            "total_posts": len(facebook_posts),
            "platform": "facebook"
        }
        
    except Exception as e:
        error_msg = f"Error transforming Facebook posts: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "message": error_msg,
            "posts_transformes": 0,
            "platform": "facebook"
        }, 500

@app.post("/predict_facebook")
def predict_facebook():
    """Analyze transformed Facebook posts"""
    db = connecter_mongodb(MONGODB_URI, DB_NAME)
    facebook_posts = list(db.post_transformed_facebook.find({}))
    
    predicted_count = 0
    for i, post in enumerate(facebook_posts, 1):
            logger.debug(f"Processing post {i}/{len(facebook_posts)}")
            transformed_text = post.get('transformed_text', '')
            if not transformed_text:
                    logger.debug(f"Post {i}: No content to process")
                    continue
                
            if transformed_text:
                    sentiment = predict_sentiment(transformed_text)
                    logger.info("Sentiment prediction complete")
                    theme = predict_theme(transformed_text)
            logger.info("Theme prediction complete")
            charger_prediction_facebook(db, transformed_text, theme, sentiment)
            predicted_count += 1
    
    return {
        "message": "Facebook prediction complete",
        "posts_analyses": predicted_count,
        "platform": "facebook"
    }


@app.post("/transform_twitter")
def transform_twitter():
    """Transform all raw Twitter posts"""
    db = connecter_mongodb(MONGODB_URI, DB_NAME)
    twitter_posts = list(db.post_brut_twitter.find({}))
    
    transformed_count = 0
    for post in twitter_posts:
        content = post.get('text', '')
        if content:
            post_transformed = nettoyage(content)
            post_transformed = normaliser_text(post_transformed)
            
            charger_transformed_twitter(db, content, post_transformed)
            transformed_count += 1
    
    return {
        "message": "Twitter transformation complete",
        "posts_transformes": transformed_count,
        "platform": "twitter"
    }

@app.post("/predict_twitter")
def predict_twitter():
    """Analyze transformed Twitter posts"""
    db = connecter_mongodb(MONGODB_URI, DB_NAME)
    twitter_posts = list(db.post_transformed_twitter.find({}))
    
    predicted_count = 0
    for post in twitter_posts:
        transformed_text = post.get('transformed_text', '')
        if transformed_text:
            sentiment = predict_sentiment(transformed_text)
            theme = predict_theme(transformed_text)
            
            charger_prediction_twitter(db, transformed_text, theme, sentiment)
            predicted_count += 1
    
    return {
        "message": "Prédiction Twitter terminée", 
        "posts_analyses": predicted_count,
        "platform": "twitter"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)