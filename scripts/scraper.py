import os
import requests
import json
import re
import hashlib
import time
from bs4 import BeautifulSoup



params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "explaintext": 1,
    "redirects": 1,
    "titles": "TITLE"
}

headers = {
    "User-Agent": "MyFinanceApp/1.0 (contact: kacembarhoumi@gmail.com)"
}





DATA_DIR = "data/clean"
SOURCE_JSON = "url_by_topic.json"
MAX_PAGE_PER_TOPIC = 30
REQUEST_DELAY = 1.5
TIMEOUT = 20
USER_AGENT = "FinanceEducationBot/1.0"


def load_files() -> dict:
    with open(SOURCE_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)
    



def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def text_hash(text:str)-> str:
    return hashlib.sha1(text.encode('utf-8')).hexdigest()

def url_to_filename(url:str)-> str:
    clean = url.replace('https://', '').replace('http://', '')
    clean = re.sub(r'[^\w\-]', '_', clean)
    url_hash = text_hash(url)[:8]
    return f"{clean}_{url_hash}.txt"


def fetch_html (url:str) -> str | None:
    try:
        response = requests.get(url, headers= {'User-Agent' : USER_AGENT}, timeout=TIMEOUT)
        print("  status:", response.status_code)
        print("  content-type:", response.headers.get("Content-Type", ""))


        if response.status_code != 200:
            print("CODE STATUS ERROR")
            return None
        content_type = response.headers.get("Content-Type", "")
        print("DEBUG content_type repr:", repr(content_type))

        if ("text/html" not in content_type.lower()) and ("application/xhtml+xml" not in content_type):
            print("REJECT not html:", content_type)
            return None

        html= response.text
        if not html or len(html)<30:
            print("too short or empty text")
            return
        
        
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_text(html:str, url:str) -> tuple[str, str]:
    soup = BeautifulSoup(html,"html.parser")
    title = '' 
    if soup.title:
        title = soup.title.get_text().strip()
    main_content = find_content_container(soup, url)
    cleaned_text = clean_html_text(main_content)
    return title, cleaned_text

def find_content_container(soup, url):
    
    if 'wikipedia.org' in url:
        content = soup.find('div', id='mw-content-text')
        if content:
            return content
    
    for tag in ['article', 'main']:
        content = soup.find(tag)
        if content:
            return content
    
    return soup.body if soup.body else soup


def clean_html_text(container) -> str:
    
    
    for tag in container.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    text = container.get_text(separator='\n')
    
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    
    cleaned = '\n'.join(lines)
    
    cleaned = re.sub(r' +', ' ', cleaned)
    
    return cleaned

def is_useful_content(text: str, url: str) -> bool:

    # Minimum length check
    min_length = 800 if 'wikipedia.org' in url else 600
    if len(text) < min_length:
        return False
    
    lines = text.splitlines()
    short_lines = sum(1 for line in lines if len(line) < 30)
    
    if lines and (short_lines / len(lines)) > 0.6:
        return False
    
    return True

def save_document(topic: str, url: str, title: str, content: str) -> str:
    
    # Create topic directory
    topic_dir = os.path.join(DATA_DIR, topic)
    os.makedirs(topic_dir, exist_ok=True)
    
    filename = url_to_filename(url)
    filepath = os.path.join(topic_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"TITLE: {title}\n")
        f.write(f"SOURCE: {url}\n")
        f.write(f"TOPIC: {topic}\n")
        f.write("\n")
        f.write(content)
    
    return filepath


def crawl_topic(topic: str, urls: list[str]):

    
    print(f"\n{'='*60}")
    print(f"Crawling topic: {topic}")
    print(f"{'='*60}")
    
    
    seen_urls = set()       # URLs we've visited
    seen_hashes = set()     # Content hashes we've saved
    saved_count = 0         # How many documents saved
    
    for url in urls:
        # Check limit
        if saved_count >= MAX_PAGE_PER_TOPIC:
            print(f"Reached limit of {MAX_PAGE_PER_TOPIC} pages")
            break
        
        # Skip duplicates
        if url in seen_urls:
            print(f"Skipping (already visited): {url}")
            continue
        
        seen_urls.add(url)
        print(f"\n Processing: {url}")
        
        # Fetch HTML
        html = fetch_html(url)
        if not html:
            print("Failed to fetch HTML")
            continue
        

        time.sleep(REQUEST_DELAY)
        
        
        title, content = clean_text(html, url)
        
        # Quality check
        if not is_useful_content(content, url):
            print(" Skipping (low quality content)")
            continue
        
        # Duplicate content check
        content_hash = text_hash(content)
        if content_hash in seen_hashes:
            print("Skipping (duplicate content)")
            continue
        
        seen_hashes.add(content_hash)
        
        # Save it!
        filepath = save_document(topic, url, title, content)
        saved_count += 1
        
        print(f" Saved [{saved_count}]: {filepath}")
        print(f"   Title: {title[:50]}...")
        print(f"   Length: {len(content)} characters")
    
    print(f"\n{'='*60}")
    print(f"Topic '{topic}' complete: {saved_count} documents saved")
    print(f"{'='*60}")



def main():
    print("content scraping is starting...\n")
    ensure_dir()
    print(f"data directory {DATA_DIR} is ready")
    try:
        sources = load_files()
        print(f"url souces are loaded from {SOURCE_JSON}")
    except FileNotFoundError:
        print(f"Error: {SOURCE_JSON} is not found")
        return
    except json.JSONDecodeError:
        print("INVALID JSON")
        return
    
    total_topics = len(sources)
    topic_number = 1
    for topic in sources:
        urls = sources[topic]
        print(f"\n {topic_number}/ {total_topics}")
        crawl_topic(topic,urls)
    

    print("\n" + "="*60)
    print("🎉 Scraping complete!")
    print(f"Check your data in: {DATA_DIR}/")
    print("="*60)



if __name__ == "__main__":
    main()
