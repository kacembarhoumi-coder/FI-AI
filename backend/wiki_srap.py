import requests




headers = {
    "User-Agent": "MyFinanceApp/1.0 (contact: kacembarhoumi@gmail.com)"
}





def wikiScrape(API:str, TITLE:str, params) -> str:
    response = requests.get(API, params=params, headers=headers, timeout=20)
    response.raise_for_status

    data = response.json()

    page = next(iter(data["query"]["page"].values()))
    full_text = page.get("extract", "")
    return full_text

def clean(content:str) -> str:
    clean_text = content.replace("\u200b", "").replace("\u200e", "").replace("\u200f", "")
    return clean_text



