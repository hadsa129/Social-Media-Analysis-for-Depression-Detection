from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import json
import csv
import random
from datetime import datetime
import os
import urllib.parse
from pymongo import MongoClient
import hashlib

# Global configuration
MONGODB_URI = "mongodb://root:root@localhost:27017/?authSource=admin"
DB_NAME = "depression_social_media"
COLLECTION_NAME = "post_brut_facebook"


# Variables globales
driver = None


# Initialize the driver
def setup_driver():
    
    global driver
    try:
        options = webdriver.ChromeOptions()
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        # Hide webdriver to avoid bot detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Chrome browser initialized successfully")
        return True
        
    except Exception as e:
        print(f"Browser initialization error: {e}", "ERROR")
        return False

def manual_login():
    """Secure manual login"""
    global driver
    print("Starting manual login procedure")
    
    try:
        driver.get('https://facebook.com')
        print("Facebook page loaded - waiting for manual login")
        
        input("MANUAL LOGIN: Log in to Facebook in the browser, then press ENTER here...")
        
        # Check login
        time.sleep(5)
        if "facebook.com" in driver.current_url and "login" not in driver.current_url:
            print("Manual login successful")
            return True
        else:
            print(" Check that you are logged in", "WARNING")
            return False
            
    except Exception as e:
        print(f"Login error: {e}", "ERROR")
        return False
# Search for #depression hashtag
def direct_hashtag_search(hashtag):
    
    global driver
    print(f"Direct access to hashtag: #{hashtag}")
    
    try:
        # Clean hashtag
        clean_hashtag = hashtag.strip().replace('#', '')
        search_url = f"https://www.facebook.com/hashtag/{clean_hashtag}"
        
        print(f"Search URL: {search_url}")
        driver.get(search_url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check if page loaded correctly
        current_url = driver.current_url
        
        if f"hashtag/{clean_hashtag}" in current_url:
            print("Hashtag page loaded successfully")
            
            # Wait for content to appear
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="article"]'))
                )
                print("Post content detected")
            except:
                print("Post content not detected immediately", "WARNING")
            
            return True
        else:
            print(f" Redirected to: {current_url}", "ERROR")
            return False
            
    except Exception as e:
        print(f"Hashtag access error: {e}", "ERROR")
        return False
# Click 'See more' for full content
def expand_see_more(element):
    
    global driver
    try:
        
        
        see_more_texts = ['voir plus', 'see more', 'plus', 'more', '… plus']
        for text in see_more_texts:
            try:
                buttons = element.find_elements(By.XPATH, f".//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                for button in buttons:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", button)
                        print(f"'See more' clicked (text: {text})")
                        time.sleep(2)
                        return True
                    except:
                        continue
            except:
                continue
        
        
        see_more_selectors = [
            'div[role="button"]',
            'span[dir="auto"]',
            'div.x1i10hfl',
            'span.x1iyjqo2',
            'a[role="button"]',
            'div.x1qjc9v5'
        ]
        
        for selector in see_more_selectors:
            try:
                buttons = element.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    try:
                        button_text = button.text.lower()
                        if any(keyword in button_text for keyword in ['voir plus', 'see more', 'plus', 'more']):
                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", button)
                            print("'See more' clicked (CSS selector)")
                            time.sleep(2)
                            return True
                    except:
                        continue
            except:
                continue
        
        print(" 'See more' button not found")
        return False
        
    except Exception as e:
        print(f"'See more' expansion error: {e}", "WARNING")
        return False
# Extract posts
def extract_post_data(element):
    
    global driver
    try:
        post_data = {}
        
        # Open full post (see more)
        expand_see_more(element)
        time.sleep(1)
        
        
        content_selectors = [
            'div[dir="auto"]',
            'div[data-ad-preview="message"]',
            'div.x1iorvi4',
            'span.x1lliihq',
            'div.x1y1aw1k',
            'div[class*="userContent"]'
        ]
        
        full_content = ""
        for selector in content_selectors:
            try:
                elements = element.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) > len(full_content):
                        full_content = text
            except:
                continue
        
        if not full_content or len(full_content) < 10:
            return None
        
        post_data['content'] = full_content
        
        # Author
        author_selectors = [
            'a[role="link"][tabindex="0"]',
            'h3 a',
            'strong a',
            'a.x1i10hfl',
            'span.x1lliihq a'
        ]
        
        for selector in author_selectors:
            try:
                authors = element.find_elements(By.CSS_SELECTOR, selector)
                for author in authors:
                    author_text = author.text.strip()
                    author_href = author.get_attribute('href')
                    if (author_text and len(author_text) > 1 and 
                        author_href and "facebook.com" in author_href):
                        post_data['author'] = author_text
                        break
                if post_data.get('author'):
                    break
            except:
                continue
        
        # Timestamp
        time_selectors = [
            'span.x4k7w5x',
            'span.x1nxh6w3',
            'abbr',
            'a.x1i10hfl span',
            'span[dir="auto"] span'
        ]
        
        for selector in time_selectors:
            try:
                time_elements = element.find_elements(By.CSS_SELECTOR, selector)
                for time_elem in time_elements:
                    time_text = time_elem.text.strip()
                    time_title = time_elem.get_attribute('title')
                    
                    if time_text and any(keyword in time_text.lower() for keyword in 
                                       ['min', 'heure', 'hour', 'day', 'jour', 'mois', 'month', 'year', 'an']):
                        post_data['time'] = time_text
                        break
                if post_data.get('time'):
                    break
            except:
                continue
        
        # 5. Unique ID with timestamp to avoid duplicates
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        content_for_id = str(post_data.get('content', '')) + str(post_data.get('author', '')) + str(post_data.get('time', '')) + timestamp_str
        post_data['post_id'] = hashlib.md5(content_for_id.encode('utf-8')).hexdigest()
        
        # 6. Basic metadata
        
        print(f" Post extracted - Author: {post_data.get('author', 'N/A')}")
        
        return post_data
        
    except Exception as e:
        print(f"Extraction error: {e}", "WARNING")
        return None

def save_to_mongodb(posts):
    """Save posts to MongoDB with unique ID each time"""
    if not posts:
        print("No posts to save", "WARNING")
        return 0
    
    client = None
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            socketTimeoutMS=30000,
            connectTimeoutMS=10000
        )
        
        # Tester la connexion
        client.admin.command('ping')
        print("Connexion MongoDB établie")
        
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Préparer les documents pour MongoDB
        mongo_docs = []
        saved_count = 0
        
        for i, post in enumerate(posts):
            try:
             
                unique_timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f") + str(i)
                unique_id = hashlib.md5(unique_timestamp.encode('utf-8')).hexdigest()
                
               
                mongo_doc = {
                    '_id': unique_id,  
                    'content': post.get('content', ''),
                    'author': post.get('author', ''),
                    'time': post.get('time', ''),
                    'post_id': post.get('post_id', ''),
                    
                }
                mongo_docs.append(mongo_doc)
                saved_count += 1
                
            except Exception as e:
                print(f"Erreur préparation post: {e}", "WARNING")
                continue
        
       
        if mongo_docs:
            try:
                result = collection.insert_many(mongo_docs, ordered=False)
                saved_count = len(result.inserted_ids)
                print(f"{saved_count} posts sauvegardés dans MongoDB")
                return saved_count
            except Exception as e:
                print(f" Erreur insertion MongoDB: {e}", "ERROR")
                return 0
        else:
            return 0
                
    except Exception as e:
        print(f" Erreur MongoDB: {e}", "ERROR")
        return 0
    finally:
        if client:
            client.close()

def extract_visible_posts():
   
    global driver
    posts_data = []
    
    post_selectors = [
        'div[role="article"]',
        'div.x1yztbdb',
        'div.x1iorvi4',
        'div[data-ad-preview="message"]'
    ]
    
    for selector in post_selectors:
        try:
            posts = driver.find_elements(By.CSS_SELECTOR, selector)
            for post in posts:
                try:
                    post_data = extract_post_data(post)
                    if post_data and post_data.get('content'):
                        posts_data.append(post_data)
                except Exception as e:
                    continue
            if posts_data:
                break
        except:
            continue
    
    return posts_data
# Scroll to load more posts
def perform_scroll():
   
    global driver
    try:
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
    except Exception as e:
        print(f"Error while scrolling: {e}", "WARNING")

# To scroll through all possible posts
def smart_scroll(max_posts=300, max_scrolls=100):
    
    print(f"Starting scraping - Target: {max_posts} posts")
    
    all_posts = []
    scroll_count = 0
    no_new_posts_count = 0
    
    try:
        while (len(all_posts) < max_posts and 
               scroll_count < max_scrolls and 
               no_new_posts_count < 10):
            
            scroll_count += 1
            print(f"Scroll #{scroll_count} - Posts: {len(all_posts)}/{max_posts}")
            
            # Extraire les posts visibles
            current_posts = extract_visible_posts()
            
            if current_posts:
                # Ajouter TOUS les posts
                all_posts.extend(current_posts)
                
                # Sauvegarde immédiate dans MongoDB
                saved_count = save_to_mongodb(current_posts)
                
                new_count = len(current_posts)
                print(f" {new_count} posts extraits ({saved_count} sauvegardés)")
                no_new_posts_count = 0
            else:
                no_new_posts_count += 1
                print(f"ℹ  Aucun nouveau post ({no_new_posts_count}/10)")
            
            
            # Scrolling
            perform_scroll()
            
            # Vérifier si on a atteint la limite
            if len(all_posts) >= max_posts:
                break
            
            time.sleep(random.uniform(3, 6))  # Délai plus long entre les scrolls
        
        # Sauvegarde finale
        if all_posts:
            
            final_saved = save_to_mongodb(all_posts)
            print(f"💾 Sauvegarde finale: {final_saved} posts dans MongoDB")
        
        print(f" Scraping terminé - {len(all_posts)} posts collectés")
        return all_posts
        
    except Exception as e:
        print(f" Erreur lors du scraping: {str(e)}", "ERROR")
        if all_posts:
           
            save_to_mongodb(all_posts)
        return all_posts

def close_driver():
    global driver
    print("Fermeture du navigateur")
    if driver:
        driver.quit()

def main():
   
   
    
    if not setup_driver():
        return
    
    try:
        #  Connexion
        if not manual_login():
            return
        
        #  chercher hashtag
        hashtag = "depression"
        if not direct_hashtag_search(hashtag):
            print("Échec accès hashtag", "ERROR")
            return
        
        # Scrolling automatique 
        posts = smart_scroll(max_posts=400, max_scrolls=150)
        
        print(" SCRAPING TERMINÉ AVEC SUCCÈS!")
        
    except KeyboardInterrupt:
        print(" Interruption par l'utilisateur", "WARNING")
    except Exception as e:
        print(f" Erreur: {e}", "ERROR")
    finally:
        close_driver()

if __name__ == "__main__":
    main()