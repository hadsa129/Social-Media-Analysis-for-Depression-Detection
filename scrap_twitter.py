from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium. webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import time
import json
import random
import os
from datetime import datetime
from loguru import logger
# Scroll the page to load more tweets
def scroll_page(driver, scroll_pause_time=1):
    
    scroll_count = 0
    
    while True:  # Boucle infinie
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(scroll_pause_time)
        
        scroll_count += 1
        
        if scroll_count % 10 == 0:
            print(f"Scrolling {scroll_count}")

# Configuration MongoDB
MONGODB_URI = "mongodb://root:root@localhost:27017/?authSource=admin"
DB_NAME = "depression_social_media"

# Save scraped tweets to MongoDB
def sauvegarder_tweets_mongodb(tweets):
   
    if not tweets:
        logger.warning("No tweets to save")
        return False
    
    client = None
    try:
        # Establish connection
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        # Log in to Twittering collections
        db.list_collection_names()
        logger.info(f"Successfully connected to database {DB_NAME}")
        
        # Check if the collection exists, otherwise create it
        if "post_brut_twitter" not in db.list_collection_names():
            db.create_collection("post_brut_twitter")
        
        # Check if the tweets already exist to avoid duplicates
        existing_ids = set(db.post_brut_twitter.distinct("id"))
        new_tweets = [t for t in tweets if t.get('id') not in existing_ids]
        
        if not new_tweets:
            logger.info("All tweets already exist in the database")
            return True
            
        # Insert new tweets
        result = db.post_brut_twitter.insert_many(new_tweets)
        logger.success(f"{len(result.inserted_ids)} new tweets saved in MongoDB")
        return True
        
    except Exception as e:
        logger.error(f"Error during saving in MongoDB: {str(e)}")
        return False
        
    finally:
        # Always close the connection
        if client is not None:
            client.close()
# Check if browser is still active
def is_browser_alive(driver):
    
    try:
        driver.current_url
        return True
    except:
        return False
# Get tweets
def get_tweets(driver):
    
    tweets = []
    scroll_count = 0
    error_count = 0
    max_errors = 10  # Increase the number of allowed errors
    

    try:
        while error_count < max_errors:
            try:
                # Check if the browser is still active
                if not is_browser_alive(driver):
                  
                    break
                
                scroll_count += 1
                
                # Scroll and wait 1 second
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Every 5 iterations, try to click on "Show more replies"
                if scroll_count % 5 == 0:
                    try:
                        more_replies = driver.find_elements(
                            By.XPATH, 
                            "//div[@role='button' and (contains(., 'Voir plus de réponses') or contains(., 'Show more replies'))]"
                        )
                        for btn in more_replies[-3:]:
                            try:
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(0.5)
                            except:
                                continue
                    except:
                        pass
                
                if True:
                    try:
                        tweet_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((
                                By.CSS_SELECTOR, 
                                'article[data-testid="tweet"], article[role="article"], div[data-testid="tweet"]'
                            ))
                        )
                        
                        new_tweets = 0
                        for tweet in tweet_elements:
                            try:
                                tweet_id = (
                                    tweet.get_attribute('data-tweet-id') or 
                                    tweet.get_attribute('data-item-id') or 
                                    str(random.randint(100000, 999999))  # Random ID for tweets without ID
                                )
                                
                                # Get the tweet text
                                try:
                                    text_elem = tweet.find_element(By.CSS_SELECTOR, 'div[lang], div[data-testid="tweetText"]')
                                    text = text_elem.text
                                except:
                                    text = "Text not available"
                                
                                # Get the username
                                try:
                                    user_elem = tweet.find_element(
                                        By.CSS_SELECTOR, 
                                        'div[data-testid="User-Name"], [data-testid="User-Name"]'
                                    )
                                    user = user_elem.text.split('\n')[0].strip()
                                except:
                                    user = f"Unknown_user_{random.randint(1000, 9999)}"
                                
                                # Get the date
                                try:
                                    time_elem = tweet.find_element(By.TAG_NAME, 'time')
                                    timestamp = time_elem.get_attribute('datetime')
                                except:
                                    timestamp = datetime.now().isoformat()
                                
                                
                                clean_user = user.split('\n')[0].strip().split('@')[-1]
                                
                                tweet_data = {
                                    'user': clean_user,
                                    'text': text,
                                    'timestamp': timestamp,
                                    'id': tweet_id
                                }
                                tweets.append(tweet_data)
                                new_tweets += 1
                                
                            except Exception as e:
                                continue 
                        
                   
                        current_count = len(tweets)
                        print(f"\rTweets collected: {current_count} (New: {new_tweets})", end='', flush=True)
                        
                        error_count = 0
                        
                    except Exception as e:
                        error_count += 1
                        error_msg = str(e)[:200]
                        print(f"\nError while searching for tweets (Error {error_count}/{max_errors}): {error_msg}...")
                        time.sleep(2)
                        if not is_browser_alive(driver):
                            print("Browser is no longer responding. Stopping...")
                            break
                        continue
                
            except Exception as e:
                error_count += 1
                print(f"\nError in the main loop (Error {error_count}/{max_errors}): {str(e)[:200]}...")
                time.sleep(2)
                if not is_browser_alive(driver):
                    print("Browser is no longer responding. Stopping...")
                    break
    
    except KeyboardInterrupt:
        print("\n\nStopping the collection by the user...")
    
    if tweets:
        try:
            filename = f"tweets_depression_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)
            print(f"\n {len(tweets)} tweets have been saved in {filename}")
        except Exception as e:
            print(f"\nError while saving: {str(e)}")
    else:
        print("\nNo tweets were collected.")
    
    return tweets

def main():
    # Initialize the driver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size=1200,800")
    
    # Browser configuration logs
   
    logger.info("Starting the Twitter scraping script")
    
    try:
        # Initialize the browser with timeout management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  
        driver.set_script_timeout(30)     
        driver.implicitly_wait(10)        
        driver.maximize_window()
        
        # Hide WebDriver to avoid robot detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Step 1: Manual login (to avoid robot detection, start with manual login)
        print("Opening Twitter...")
        driver.get("https://x.com/login")
        
        print("\nPlease log in manually...")
        print("Once logged in, press Enter in this terminal to continue...")
        input("Press Enter after logging in...")
        
        # Step 2: Automatic search for #depression
        print("\nSearching for #depression...")
        search_url = "https://x.com/search?q=%23depression&src=typed_query&f=live"
        driver.get(search_url)
      
        time.sleep(5)
        
        # Get tweets 
        print("\nStarting the continuous collection of tweets...")
        print("Press Ctrl+C to stop the collection at any time\n")
        
      
        tweets = get_tweets(driver)
        
        
        if tweets:
            print(f"\n\nCollection finished. {len(tweets)} tweets were collected in total.")
            
            # Save tweets to MongoDB
            print("\nSaving tweets to MongoDB...")
            if sauvegarder_tweets_mongodb(tweets):
                print("Tweets have been saved successfully in MongoDB")
            else:
                print("Error while saving in MongoDB")
            
        else:
            print("\nNo tweets were retrieved. Check your connection or try again later.")
        
        # Wait for page to load
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("Navigateur fermé.")

if __name__ == "__main__":
    main()