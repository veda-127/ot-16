from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import re

# Initialize Flask app
app = Flask(__name__)

# File to store scraped tweets
CSV_FILE = "tweets_data.csv"

# Function to extract hashtags from tweets
def extract_hashtags(text):
    return re.findall(r"#\w+", text)

# Function to scrape tweets from Nitter
def scrape_nitter_hashtag(hashtag, duration=60):
    """Scrapes tweets for a given hashtag and stores them in a CSV file."""
    
    # Setup ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Nitter search URL
    nitter_url = f"https://nitter.net/search?q=%23{hashtag}"
    driver.get(nitter_url)

    start_time = time.time()
    seen_tweets = set()  # Store already collected tweets
    tweets_list = []  # List to store tweets for saving

    try:
        while time.time() - start_time < duration:
            wait = WebDriverWait(driver, 10)
            tweets = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tweet-content media-body']")))

            for tweet in tweets:
                text = tweet.text.strip()
                hashtags = extract_hashtags(text)
                if text not in seen_tweets:  # Avoid duplicates
                    seen_tweets.add(text)
                    tweets_list.append({"hashtag": hashtag, "tweet": text, "hashtags": ",".join(hashtags)})  # Store hashtags

            # Scroll to load more tweets
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(1)  # Allow time to load new tweets

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()
        save_tweets_to_csv(tweets_list)
        print(f"✅ {len(tweets_list)} tweets added to {CSV_FILE}")
        return tweets_list

def save_tweets_to_csv(tweets_list):
    """Saves tweets to a CSV file."""
    df = pd.DataFrame(tweets_list)
    
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_csv(CSV_FILE, index=False, encoding="utf-8")
    print(f"✅ Tweets saved to {CSV_FILE}")

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        hashtag = request.form.get("hashtag")
        if not hashtag:
            return render_template("index.html", error="Hashtag is required")

        # Scrape tweets for the given hashtag
        tweets = scrape_nitter_hashtag(hashtag)
        return redirect(url_for("results", hashtag=hashtag))

    return render_template("index.html")

@app.route("/results")
def results():
    hashtag = request.args.get("hashtag")
    if not hashtag:
        return redirect(url_for("index"))

    # Load scraped tweets from CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["hashtag", "tweet", "hashtags"])

    # Filter tweets for the given hashtag
    tweets = df[df["hashtag"] == hashtag]["tweet"].tolist()
    return render_template("results.html", hashtag=hashtag, tweets=tweets)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
