from bs4 import BeautifulSoup
import requests

url = 'https://jewelers.services/productcore/api/pl/Jewelry-Rings-2/'

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 "
                  "Safari/537.36"
}
body = {"filters": [{"key": "ItemsPerPage", "value": "36"}], "page": 1,
        "sortCode": 28420, "path": "Jewelry-Rings-2·Stone-Rings"}
response = requests.post(url, headers=headers, json=body)
src = response.json()
# soup = BeautifulSoup(src, "lxml")
# products = soup.find_all("Style")
result_list = []
for item in src["IndexedProducts"]["Results"]:
    result_list.append(
        {
            "Style": item.get("Style"),
            "URLDescription": item.get("URLDescription"),
        }
    )

product_url = "https://jewelers.services/productcore/api/pd/"


def parse_description(URLDescription, Style):
    product_url = f"https://jewelers.services/productcore/api/pd/{URLDescription}/{Style}"
