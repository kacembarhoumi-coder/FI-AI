import os, json, re, time, hashlib
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


SOURCES_JSON = "scripts/url_by_topic.json"
CLEAN_ROOT = "data/clean"
RAW_ROOT = "data/raw"

MAX_PAGE_PER_TOPIC = 30
REQUEST_DELAY = 1.2
TIMEOUT = 20
USER_AGENT = "finance-rag-scraper/1.0 (educational)"

# Phase 2 expansion limit per seed page (kept small on purpose)
EXPAND_LINKS_PER_SEED = 6


# -------------------------
# STEP A: filesystem + utils
# -------------------------
def ensure_dirs():
    os.makedirs(CLEAN_ROOT, exist_ok=True)
    os.makedirs(RAW_ROOT, exist_ok=True)

def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def domain(url: str) -> str:
    return urlparse(url).netloc.lower()

def safe_slug(url: str) -> str:
    parsed = urlparse(url)
    d = parsed.netloc.replace(".", "_")
    path = re.sub(r"[^a-zA-Z0-9]+", "_", parsed.path.strip("/").lower())
    if not path:
        path = "root"
    h = sha1(url)[:8]
    return f"{d}__{path}__{h}.txt"

def normalize_url(base: str, href: str) -> str:
    u = urljoin(base, href)
    u = u.split("#")[0]
    return u


# -------------------------
# STEP B: load sources
# -------------------------
def load_sources() -> dict:
    with open(SOURCES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# STEP C: fetch HTML
# -------------------------
def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "text/html" not in ctype:
            return None
        return r.text
    except Exception:
        return None


# -------------------------
# STEP D: extraction (domain-aware)
# -------------------------
def extract_main_container(soup: BeautifulSoup, url: str):
    d = domain(url)

    # Wikipedia: main content lives here
    if "wikipedia.org" in d:
        main = soup.select_one("#mw-content-text")
        if main:
            return main

    # Generic good targets
    for selector in ["article", "main"]:
        main = soup.select_one(selector)
        if main:
            return main

    return soup.body or soup


def clean_text_from_container(container) -> str:
    # remove noise tags inside container
    for tag in container.find_all(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = container.get_text(separator="\n")

    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    return cleaned


def extract_clean_text(html: str, url: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")

    title = ""
    if soup.title and soup.title.get_text():
        title = soup.title.get_text().strip()

    container = extract_main_container(soup, url)
    cleaned = clean_text_from_container(container)

    return title, cleaned


# -------------------------
# STEP E: quality gates
# -------------------------
BAD_URL_KEYWORDS = [
    "privacy", "terms", "contact", "about", "cookies", "subscribe",
    "login", "signin", "signup", "advert", "careers"
]

def looks_like_content_url(url: str) -> bool:
    """Keep only URLs that look like 'content pages'."""
    u = url.lower()
    if any(k in u for k in BAD_URL_KEYWORDS):
        return False

    d = domain(url)
    path = urlparse(url).path.lower()

    # Wikipedia: only /wiki/ pages (avoid /special, etc.)
    if "wikipedia.org" in d:
        return path.startswith("/wiki/") and (":" not in path)  # filter Special:, File:, etc.

    # Investopedia: terms + articles are often good
    if "investopedia.com" in d:
        return path.startswith("/terms/") or path.startswith("/articles/")

    # FINRA: investor education tends to be under /investors/
    if "finra.org" in d:
        return path.startswith("/investors/")

    # investor.gov: educational sections
    if "investor.gov" in d:
        return "/introduction-investing/" in path

    # CME education pages usually contain /education/
    if "cmegroup.com" in d:
        return "/education/" in path

    # Default: allow, but Phase 2 is still small
    return True


def is_useful_text(text: str, url: str) -> bool:
    """
    Reject junk pages that are mostly navigation or too short.
    """
    if "wikipedia.org" in url:
        return len(text) >= 800
    if len(text) < 900:  # stronger than your previous 600
        return False

    # Too many very short lines often indicates menus
    lines = text.splitlines()
    short_lines = sum(1 for ln in lines if len(ln) <= 25)
    if lines and (short_lines / max(len(lines), 1)) > 0.65:
        return False

    return True


# -------------------------
# STEP F: link discovery (filtered)
# -------------------------
def discover_links(seed_url: str, html: str, limit: int) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    base_domain = domain(seed_url)

    links: list[str] = []
    for a in soup.find_all("a", href=True):
        u = normalize_url(seed_url, a["href"])
        if not u:
            continue
        if domain(u) != base_domain:
            continue
        if u in links:
            continue
        if not looks_like_content_url(u):
            continue

        links.append(u)
        if len(links) >= limit:
            break

    return links


# -------------------------
# STEP G: save docs
# -------------------------
def save_doc(topic: str, url: str, title: str, cleaned: str) -> str:
    topic_dir = os.path.join(CLEAN_ROOT, topic)
    os.makedirs(topic_dir, exist_ok=True)

    filename = safe_slug(url)
    out_path = os.path.join(topic_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\n")
        f.write(f"SOURCE: {url}\n")
        f.write(f"TOPIC: {topic}\n")
        f.write("DATE: unknown\n\n")
        f.write(cleaned)

    return out_path


# -------------------------
# STEP H: crawl topic (SEEDS FIRST)
# -------------------------
def crawl_topic(topic: str, seed_urls: list[str]):
    print(f"\n=== Topic: {topic} ===")

    seen_urls = set()
    seen_hashes = set()
    saved = 0

    # Phase 1: scrape seeds only (high quality)
    candidate_links: list[str] = []

    for url in seed_urls:
        if saved >= MAX_PAGE_PER_TOPIC:
            break
        if url in seen_urls:
            continue
        seen_urls.add(url)

        html = fetch_html(url)
        time.sleep(REQUEST_DELAY)
        if html is None:
            print(f"skip seed (fetch failed): {url}")
            continue

        title, cleaned = extract_clean_text(html, url)
        if not is_useful_text(cleaned, url):
            print(f"skip seed (low quality): {url}")
            continue

        h = sha1(cleaned)
        if h in seen_hashes:
            print(f"skip seed (duplicate): {url}")
            continue
        seen_hashes.add(h)

        out_path = save_doc(topic, url, title, cleaned)
        saved += 1
        print(f"[seed {saved}] saved -> {out_path}")

        # collect candidates for Phase 2 (small, filtered)
        candidate_links.extend(discover_links(url, html, limit=EXPAND_LINKS_PER_SEED))

    # Phase 2: scrape only filtered candidates AFTER seeds
    for url in candidate_links:
        if saved >= MAX_PAGE_PER_TOPIC:
            break
        if url in seen_urls:
            continue
        seen_urls.add(url)

        html = fetch_html(url)
        time.sleep(REQUEST_DELAY)
        if html is None:
            continue

        title, cleaned = extract_clean_text(html, url)
        if not is_useful_text(cleaned):
            continue

        h = sha1(cleaned)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        out_path = save_doc(topic, url, title, cleaned)
        saved += 1
        print(f"[expand {saved}] saved -> {out_path}")


def main():
    print("✅ scraper started (seeds-first)")
    ensure_dirs()

    sources = load_sources()
    for topic, seeds in sources.items():
        crawl_topic(topic, seeds)

    print("\n Done. Check data/clean/<topic>/")

if __name__ == "__main__":
    main()
