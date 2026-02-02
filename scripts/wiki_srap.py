import requests

API = "https://en.wikipedia.org/w/api.php"
TITLE = "Financial_market"

headers = {
    "User-Agent": "MyFinanceApp/1.0 (contact: kacembarhoumi@gmail.com)"
}

params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "explaintext": 1,
    "redirects": 1,
    "titles": TITLE
}

response = requests.get(API, params=params, headers=headers, timeout=20)
response.raise_for_status()

data = response.json()

page = next(iter(data["query"]["pages"].values()))
full_text = page.get("extract", "")



full_text_clean = full_text.replace("\u200b", "").replace("\u200e", "").replace("\u200f", "")
print(full_text_clean)
with open("financial_market.txt", "w") as f:
    f.write(full_text_clean)


def wikiScrape(API:str) -> str:
    response = requests.get(API, params=params, headers=headers, timeout=20)