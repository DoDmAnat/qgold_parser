import os
import time
from datetime import datetime

import pandas as pd
import requests

BASE_URL = 'https://jewelers.services/productcore/api/'
BASE_MEDIA_URL = 'https://images.jewelers.services'

CATEGORIES = ("Jewelry-Rings-2·Stone-Rings", "Jewelry-Rings-Adjustable")
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 "
                  "Safari/537.36"
}


def get_urls(url, headers, category):
    """
    Возвращает список эндпоинтов каждого товара на странице.
    """
    body = {
        "filters": [{"key": "ItemsPerPage", "value": "36"}],
        "page": 1,
        "sortCode": 28420,
        "path": f"{category}"
    }
    response = requests.post(url, headers=headers, json=body)
    src = response.json()

    return [
        f"{BASE_URL}pd/{item.get('URLDescription')}/{item.get('Style')}"
        for item in src["IndexedProducts"]["Results"]
    ]


def get_data(url, headers):
    """Получает и возвращает данные по указанному URL-адресу в формате JSON"""
    try:
        with requests.Session() as session:
            response = session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Не удалось получить данные по адресу {url}: {str(e)}")
        return None


def get_specification(url, headers, category):
    data_table = []
    for item_url in get_urls(url, headers, category):
        print(f"Получение данных по адресу: {item_url}")
        data = get_data(item_url, headers)
        if data:
            description = {}
            product = data.get("Product")
            if product:
                description["Product"] = product["Style"]
                description["CountryOfOrigin"] = product[
                    "CountryOfOrigin"]
                description["Product availability"] = "In Stock" if \
                    product["InStock"] > 0 else "Out of Stock"
            specifications = data.get("Specifications")
            if specifications:
                description.update(
                    {spec_item["Specification"]: spec_item["Value"] for
                     spec_item in specifications})
            sizes = data.get("Sizes")
            if sizes:
                description["Price_on_size"] = [
                    {'size': size['Size'], 'MSRP': size['MSRP']} for size in
                    sizes]
            images = data.get("Images")
            if images:
                description["Images"] = {
                    f"{BASE_MEDIA_URL}/qgrepo/{img.get('FileName')}"
                    for img in images
                }
                video = data.get("Video")
                if video:
                    description[
                        "Video"] = f"{BASE_MEDIA_URL}/0/Videos/{video['FileName']}"
            data_table.append(description)
    return data_table


def save_in_excel(data, category):
    """Создание файла .xlsx и заполнение его данными"""
    df = pd.DataFrame(data)
    directory = "./output"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f'{category}.xlsx')
    df.to_excel(file_path, index=False)


def cyclic_parse(url, headers, category, interval):
    """Выполнение парсинга с заданной периодичностью"""

    print("Начало парсинга")
    data = get_specification(url, headers, category)
    save_in_excel(data, category)
    print("Данные сохранены. Ожидание следующего цикла")


if __name__ == '__main__':
    now = datetime.now()
    cyclic_parse(BASE_URL + f"pl/{CATEGORIES[0]}", HEADERS, CATEGORIES[0], 1)
    cyclic_parse(BASE_URL + f"pl/{CATEGORIES[1]}", HEADERS, CATEGORIES[1], 1)
    end = datetime.now() - now
    print(end)
