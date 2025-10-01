import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

SITEMAP_URL = "https://basecamp.com/sitemap.xml"

def get_handbook_links():
    r = requests.get(SITEMAP_URL)
    r.raise_for_status()
    # Ensure correct decoding to avoid mojibake
    if not r.encoding or r.encoding.lower() != "utf-8":
        r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "xml")
    urls = [loc.text for loc in soup.find_all("loc")]
    # Only handbook pages, but not the root
    return [u for u in urls if u.startswith("https://basecamp.com/handbook/")]

def scrape_page(url):
    r = requests.get(url)
    r.raise_for_status()
    # Ensure correct decoding to avoid mojibake
    if not r.encoding or r.encoding.lower() != "utf-8":
        r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.title.string.strip() if soup.title else url
    content = soup.select_one("div.content")
    if not content:
        return {"url": url, "title": title, "sections": {}}

    sections = {}
    current_heading = f"{title} — introduction"
    current_text = []

    for el in content.find_all(["p", "ul", "ol", "h2", "h3"], recursive=True):
        if el.name in ["h2", "h3"]:
            # store previous block if any
            if current_text:
                sections[current_heading] = "\n".join(current_text).strip()
            current_heading = el.get_text(" ", strip=True)
            current_text = []
        else:
            txt = el.get_text(" ", strip=True)
            if txt:
                current_text.append(txt)

    if current_text:
        sections[current_heading] = "\n".join(current_text).strip()

    return {"url": url, "title": title, "sections": sections}

if __name__ == "__main__":
    links = get_handbook_links()
    all_data = []
    for link in links:
        try:
            data = scrape_page(link)
            all_data.append(data)
            print(f"Scraped {link}")
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    with open("basecamp_handbook.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Saved basecamp_handbook.json")
