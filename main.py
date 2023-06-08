from openpyxl import Workbook
import pandas as pd
import requests

wb = Workbook()
ws = wb.active

url = 'https://jewelers.services/productcore/api/pl/Jewelry-Rings-2/'

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 "
                  "Safari/537.36"
}


def get_urls():
    body = {"filters": [{"key": "ItemsPerPage", "value": "36"}], "page": 1,
            "sortCode": 28420, "path": "Jewelry-Rings-2·Stone-Rings"}
    response = requests.post(url, headers=headers, json=body)
    src = response.json()

    result_list = []
    for item in src["IndexedProducts"]["Results"]:
        url_description = item.get("URLDescription")
        style = item.get("Style")
        result_list.append(
            f"https://jewelers.services/productcore/api/pd/{url_description}/{style}"
        )
    return result_list


def get_specification():
    data_table = []
    img_url = "https://images.jewelers.services/qgrepo/QR6713.jpg"
    for i in get_urls():
        response = requests.get(i, headers=headers)
        if response.status_code == 200:
            data = response.json()

            specification = {}
            for item in data:
                if item == "Product":
                    product = data.get(item)
                    specification["Product"] = product["Style"]
                    specification["CountryOfOrigin"] = product[
                        "CountryOfOrigin"]
                    specification["Product availability"] = "In Stock" if \
                        product["InStock"] > 0 else "Out of Stock"
                if item == "Specifications":
                    product = data.get(item)
                    for j in product:
                        specification[j["Specification"]] = j["Value"]
                if item == "Sizes":
                    product = data.get(item)
                    specification["Price_on_size"] = [
                        {'size': item['Size'], 'MSRP': item['MSRP']} for item
                        in
                        product]
                if item == "Images":
                    images = data.get(item)
                    specification["Images"] = {
                        f"https://images.jewelers.services/qgrepo/{img.get('FileName')}"
                        for img in images}

            data_table.append(specification)
        else:
            print(f"Failed to retrieve data from {url}")
    df = pd.DataFrame(data_table)
    df.to_excel('data.xlsx', index=False)


def get_sizes():
    data_table = []

    for i in get_urls():
        response = requests.get(i, headers=headers)
        if response.status_code == 200:
            data = response.json()
            sizes = data.get("Sizes", [])
            result = [{'size': item['Size'], 'MSRP': item['MSRP']} for item in
                      sizes]
            print(result)
            break
        #     specification = {}
        #     for size in sizes:
        #         specification[size["Size"]] = size["Value"]
        #     data_table.append(specification)
        # else:
        #     print(f"Failed to retrieve data from {url}")


get_specification()
