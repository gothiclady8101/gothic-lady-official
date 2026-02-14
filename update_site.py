import requests
import json
import datetime
import os
import re
from bs4 import BeautifulSoup

# Configuration
SUNO_USERNAME = "gothiclady1002"
SUNO_PROFILE_URL = f"https://suno.com/@{SUNO_USERNAME}"
INDEX_FILE = "index.html"

# Nitter instances to try (in order of preference)
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.lucabased.xyz",
    "https://xcancel.com"
]

def get_suno_songs():
    """
    Scrapes the Suno profile page for the latest songs using __NEXT_DATA__.
    Returns a list of dictionaries with song details.
    """
    print(f"Fetching Suno profile: {SUNO_PROFILE_URL}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(SUNO_PROFILE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suno uses Next.js, so data is often Hydrated in a script tag
        next_data_tag = soup.find('script', id='__NEXT_DATA__')
        
        songs = []
        
        if next_data_tag:
            try:
                data = json.loads(next_data_tag.string)
                # Navigate JSON path - this is heuristic and might change
                # Usually in props -> pageProps -> fallbackData or similar
                # We will look for anything that looks like a list of clips
                
                # Recursive search for 'clips' key or similar structure
                def find_clips(obj):
                    if isinstance(obj, dict):
                        if 'clips' in obj and isinstance(obj['clips'], list):
                            return obj['clips']
                        for key, value in obj.items():
                            result = find_clips(value)
                            if result: return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_clips(item)
                            if result: return result
                    return None

                clips = find_clips(data)
                
                if clips:
                    for clip in clips[:5]: # Get top 5
                        # Extract relevant fields
                        title = clip.get('title') or "Untitled"
                        clip_id = clip.get('id')
                        metadata = clip.get('metadata', {})
                        
                        # Image logic
                        image_url = clip.get('image_large_url') or clip.get('image_url')
                        if not image_url and clip_id:
                            image_url = f"https://cdn1.suno.ai/image_{clip_id}.png" # Fallback guess
                            
                        # Style/Genre logic
                        tags = metadata.get('tags') or ""
                        
                        # Date
                        created_at = clip.get('created_at') # ISO format usually
                        if created_at:
                            try:
                                dt = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                date_str = dt.strftime("%Y.%m.%d")
                            except:
                                date_str = datetime.datetime.now().strftime("%Y.%m.%d")
                        else:
                            date_str = datetime.datetime.now().strftime("%Y.%m.%d")

                        songs.append({
                            'id': clip_id,
                            'title': title,
                            'link': f"https://suno.com/song/{clip_id}",
                            'image': image_url,
                            'style': tags,
                            'date': date_str,
                            'is_public': clip.get('is_public', False)
                        })
                        print(f"Found Suno song: {title}")
                else:
                    print("Could not find 'clips' list in __NEXT_DATA__")
            except Exception as e:
                print(f"Error parsing __NEXT_DATA__: {e}")
        
        # Fallback: CSS Selectors if JSON fails
        if not songs:
            print("Trying CSS selector fallback...")
            # This is fragile but better than nothing
            song_links = soup.select('a[href^="/song/"]')
            seen_ids = set()
            
            for link in song_links:
                href = link.get('href')
                clip_id = href.split('/')[-1]
                
                if clip_id in seen_ids: continue
                seen_ids.add(clip_id)
                
                # Try to find container
                container = link.find_parent('div', class_=lambda x: x and 'relative' in x)
                if not container: container = link.parent
                
                title = link.get_text(strip=True) or "Unknown Song"
                
                # Image
                img = container.find('img')
                image_url = img.get('src') if img else ""
                
                s = {
                    'id': clip_id,
                    'title': title,
                    'link': f"https://suno.com{href}",
                    'image': image_url,
                    'style': "Gothic / AI Generated", # Default
                    'date': datetime.datetime.now().strftime("%Y.%m.%d"), # Unknown
                    'is_public': True
                }
                songs.append(s)
                if len(songs) >= 5: break

        return songs

    except Exception as e:
        print(f"Failed to fetch Suno profile: {e}")
        return []

def get_latest_tweets():
    """
    Fetches latest tweets from Nitter RSS.
    """
    username = "Rose_GothicLady"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for instance in NITTER_INSTANCES:
        rss_url = f"{instance}/{username}/rss"
        print(f"Trying Nitter: {rss_url}")
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                if not soup.find('item'):
                    soup = BeautifulSoup(response.content, 'html.parser')
                
                items = soup.find_all('item', limit=3)
                tweets = []
                for item in items:
                    # Title often contains the tweet text in RSS
                    description = item.find('description').text if item.find('description') else ""
                    title = item.find('title').text if item.find('title') else ""
                    
                    # Nitter title is usually the tweet text. Description might contain HTML images etc.
                    # We prefer the raw text.
                    text_content = title
                    
                    link = item.find('link').text if item.find('link') else "#"
                    pubDate = item.find('pubDate').text if item.find('pubDate') else ""
                    
                    try:
                        # RFC 822 date parsing
                        dt = datetime.datetime.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %Z")
                        date_str = dt.strftime("%Y.%m.%d")
                    except:
                        date_str = datetime.datetime.now().strftime("%Y.%m.%d")
                    
                    # Clean text
                    # Remove "R to @..." if it's a reply (optional, keeping it simple for now)
                    
                    tweets.append({
                        'text': text_content[:100] + "..." if len(text_content) > 100 else text_content,
                        'date': date_str,
                        'link': link
                    })
                
                if tweets:
                    print(f"Fetched {len(tweets)} tweets from {instance}")
                    return tweets
        except Exception as e:
            print(f"Failed {instance}: {e}")
            continue
            
    print("All Nitter instances failed.")
    return []

def update_index_html(new_songs, new_tweets):
    """
    Updates index.html with new content using BeautifulSoup.
    """
    if not os.path.exists(INDEX_FILE):
        print(f"{INDEX_FILE} not found!")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    modified = False

    # 1. Update News with New Songs
    news_list = soup.find("ul", class_="news-list")
    if news_list and new_songs:
        existing_news_text = news_list.get_text()
        
        # Sort songs by date (newest first) just in case
        # Assuming new_songs comes in some order, but let's process them
        
        for song in new_songs:
            # Simple check to avoid duplicate news entries
            if song['title'] in existing_news_text:
                continue
                
            print(f"Adding news for song: {song['title']}")
            new_li = soup.new_tag("li", attrs={"class": "news-item"})
            
            date_span = soup.new_tag("span", attrs={"class": "news-date"})
            date_span.string = song['date']
            
            text_span = soup.new_tag("span", attrs={"class": "news-text"})
            # Link formatting
            link = soup.new_tag("a", attrs={"href": song['link'], "target": "_blank", "style": "color: inherit; text-decoration: none;"})
            link.string = f"New Song '{song['title']}' Released."
            text_span.append(link)
            
            # Badge
            badge = soup.new_tag("span", attrs={"class": "new-badge"})
            badge.string = "NEW!"
            text_span.append(badge)
            
            new_li.append(date_span)
            new_li.append(text_span)
            
            news_list.insert(0, new_li) # Add to top
            modified = True

    # 2. Update Discography
    discography_grid = soup.find("div", class_="discography-grid")
    if discography_grid and new_songs:
        existing_html = str(discography_grid)
        
        for song in new_songs:
            if song['id'] in existing_html:
                continue
            
            print(f"Adding discography card for: {song['title']}")
            # Create Card
            # Structure:
            # <a class="song-item" href="..." target="_blank">
            #   <div class="song-jacket"><img src="..."></div>
            #   <div class="song-info"><div class="title">...</div><div class="meta">...</div></div>
            # </a>
            
            a_tag = soup.new_tag("a", attrs={"class": "song-item", "href": song['link'], "target": "_blank"})
            
            jacket_div = soup.new_tag("div", attrs={"class": "song-jacket"})
            img = soup.new_tag("img", attrs={"src": song['image'], "alt": song['title'], "loading": "lazy"})
            jacket_div.append(img)
            
            info_div = soup.new_tag("div", attrs={"class": "song-info"})
            title_div = soup.new_tag("div", attrs={"class": "title"})
            title_div.string = song['title']
            meta_div = soup.new_tag("div", attrs={"class": "meta"})
            meta_div.string = song['style'] or "Gothic / AI"
            
            info_div.append(title_div)
            info_div.append(meta_div)
            
            a_tag.append(jacket_div)
            a_tag.append(info_div)
            
            discography_grid.insert(0, a_tag) # Add to top
            modified = True

    # 3. Update X Feed
    if new_tweets:
        x_feed_container = soup.find("div", class_="x-feed-container")
        if x_feed_container:
            tweet_list = x_feed_container.find("ul", class_="tweet-list")
            if tweet_list:
                tweet_list.clear() # Remove old tweets
                
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
                
                print("Updated X Feed.")
                modified = True

    if modified:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print("Successfully updated index.html")
    else:
        print("No changes needed for index.html")

if __name__ == "__main__":
    # Main execution
    suno_songs = get_suno_songs()
    tweets = get_latest_tweets()
    
    update_index_html(suno_songs, tweets)
