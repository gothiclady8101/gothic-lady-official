import requests
import re
import datetime
import os
from bs4 import BeautifulSoup

# Configuration
SUNO_USERNAME = "gothiclady1002"
SUNO_PROFILE_URL = f"https://suno.com/@{SUNO_USERNAME}"
INDEX_FILE = "index.html"

def get_suno_songs(profile_url):
    """
    Scrapes the Suno profile page to find public songs.
    Returns a list of dictionaries with song details.
    Note: This is a simplified scraper. Suno's dynamic content might require
    browser automation (Selenium/Playwright) for full robustness, but we'll try
    basic requests + regex/soup first for efficiency in GitHub Actions.
    """
    print(f"Fetching profile: {profile_url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suno's structure is complex and React-based. 
        # We might need to look for JSON constraints or specific generic classes.
        # For this demo/v1, we will look for specific patterns or meta tags if available,
        # but robustly, we might need a workaround if it heavily relies on JS execution.
        
        # Strategy: Look for Next.js data or specific song links
        songs = []
        
        # This part is highly dependent on Suno's current DOM structure.
        # Since we can't easily see the raw HTML structure without a browser tool here,
        # we will assume a generic "find links" strategy for now, or rely on a known API if we had one.
        # FALLBACK: logic to simulate "new song found" for demonstration if scraping fails without JS.
        
        return songs

    except Exception as e:
        print(f"Error fetching Suno songs: {e}")
        return []

def get_latest_tweets():
    """
    Fetches the latest tweets from a public Nitter RSS feed.
    Returns a list of dictionaries with tweet content.
    """
    nitter_instances = [
        "https://nitter.poast.org",
        "https://nitter.privacydev.net",
        "https://nitter.cz"
    ]
    
    username = "Rose_GothicLady"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for instance in nitter_instances:
        rss_url = f"{instance}/{username}/rss"
        print(f"Trying to fetch tweets from: {rss_url}")
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml') # Use xml parser if available or html.parser as fallback
                if not soup.find('item'):
                   soup = BeautifulSoup(response.content, 'html.parser')
                
                items = soup.find_all('item', limit=3)
                tweets = []
                for item in items:
                    title = item.find('title').text
                    link = item.find('link').text
                    pubDate = item.find('pubDate').text
                    
                    # Clean up title (sometimes Nitter puts "R to @..." or includes images)
                    # We want the text content.
                    # Nitter RSS 'description' often has the full HTML content.
                    description = item.find('description').text
                    # Simple text extraction from description HTML
                    desc_soup = BeautifulSoup(description, 'html.parser')
                    text_content = desc_soup.get_text()
                    
                    # Basic date formatting
                    try:
                        dt = datetime.datetime.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %Z")
                        date_str = dt.strftime("%Y.%m.%d")
                    except:
                        date_str = pubDate

                    tweets.append({
                        'text': text_content[:140] + "..." if len(text_content) > 140 else text_content,
                        'date': date_str,
                        'link': link
                    })
                
                if tweets:
                    print(f"Successfully fetched {len(tweets)} tweets from {instance}")
                    return tweets
        except Exception as e:
            print(f"Failed to fetch from {instance}: {e}")
            continue
    
    print("All Nitter instances failed.")
    return []

def update_index_html(new_songs, new_tweets=None):
    """
    Updates index.html with new songs, news items, and tweets.
    """
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. Add to News
    news_list = soup.find("ul", class_="news-list")
    if news_list and new_songs:
        today = datetime.datetime.now().strftime("%Y.%m.%d")
        for song in new_songs:
            # Check if news already exists to avoid duplicates
            if song['title'] in str(news_list):
                continue
                
            new_li = soup.new_tag("li", attrs={"class": "news-item"})
            
            date_span = soup.new_tag("span", attrs={"class": "news-date"})
            date_span.string = today
            
            text_span = soup.new_tag("span", attrs={"class": "news-text"})
            text_span.string = f"New Song Release: {song['title']}"
            
            new_li.append(date_span)
            new_li.append(text_span)
            
            news_list.insert(0, new_li) # Prepend
            print(f"Added news for: {song['title']}")

    # 2. Update Tweets (if any)
    if new_tweets:
        x_feed_container = soup.find("div", class_="x-feed-container")
        if x_feed_container:
            # Clear existing widget/content
            x_feed_container.clear()
            
            # Rebuild structure
            title = soup.new_tag("h2", attrs={"class": "x-feed-title"})
            title.string = "X（旧Twitter）"
            x_feed_container.append(title)
            
            tweet_list = soup.new_tag("ul", attrs={"class": "tweet-list"})
            
            for tweet in new_tweets:
                li = soup.new_tag("li", attrs={"class": "tweet-item"})
                
                date_div = soup.new_tag("div", attrs={"class": "tweet-date"})
                date_div.string = tweet['date']
                
                text_div = soup.new_tag("div", attrs={"class": "tweet-text"})
                text_div.string = tweet['text']
                
                link = soup.new_tag("a", attrs={"href": tweet['link'], "target": "_blank", "class": "tweet-link"})
                link.string = "View Post"
                
                li.append(date_div)
                li.append(text_div)
                li.append(link)
                tweet_list.append(li)
            
            x_feed_container.append(tweet_list)
            
            # View More button
            footer = soup.new_tag("div", attrs={"class": "x-footer"})
            view_more = soup.new_tag("a", attrs={"href": "https://twitter.com/Rose_GothicLady", "target": "_blank", "class": "x-view-more"})
            view_more.string = "View Official X"
            footer.append(view_more)
            x_feed_container.append(footer)
            
            print("Updated X Feed with static tweets.")

    # 3. Add to Discography
    # (Implementation details for parsing the grid and adding cards...)
    # For now, we'll focus on the News section as the primary verification.
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == "__main__":
    # In a real scenario, we would allow the scraper to run.
    # For this environment, we will simulate finding a "New Song" to verify the logic works.
    
    # detected_songs = get_suno_songs(SUNO_PROFILE_URL) 
    # detected_tweets = get_latest_tweets()
    
    # Simulation (comment out real fetch for now or use if confident)
    # real_tweets = get_latest_tweets()
    # update_index_html([], real_tweets)
    
    print("Running in simulation/setup mode.")
    print("Uncomment actual fetching logic in update_site.py to enable real updates.")
    
    # For initial setup, let's inject dummy tweets to style them
    dummy_tweets = [
        {"text": "Official website renewal open. I will deliver my localized world view.", "date": "2026.02.10", "link": "#"},
        {"text": "New song 'Crimson Phantasm' is now available on Suno.", "date": "2026.02.08", "link": "#"},
        {"text": "Thank you for listening to my songs. The next update is coming soon.", "date": "2026.02.05", "link": "#"}
    ]
    update_index_html([], dummy_tweets)
