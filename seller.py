import io
import logging.config
import os
import re
import zipfile
from environs import Env

import pandas as pd
import requests

logger = logging.getLogger(__file__)


def get_product_list(last_id, client_id, seller_token):
    """
    Получить список товаров магазина озон
        Арг: 
            last_id - str. Изначально пустой, затем принимает id последнего товара
            client_id - переменная из окружения
            seller_token - АПИ токен для доступа к АПИ сайта

        Возвращает:
            Словарь в формате JSON товара

        Пример: 
            {}
  """
  
    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {
        "filter": {
            "visibility": "ALL",
        },
        "last_id": last_id,
        "limit": 1000,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")

def get_offer_ids(client_id, seller_token):
    """Получает артикулы товаров магазина озон
      Арг: 
            client_id - переменная из окружения
            seller_token - АПИ токен для доступа к АПИ сайта

        Возвращает:
            list Список из артикулов товаров

        Пример: 
            {}
    """
    last_id = ""
    product_list = []
    while True:
        some_prod = get_product_list(last_id, client_id, seller_token)
        product_list.extend(some_prod.get("items"))
        total = some_prod.get("total")
        last_id = some_prod.get("last_id")
        if total == len(product_list):
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer_id"))
    return offer_ids

def update_price(prices: list, client_id, seller_token):
    """Обновляет цены товаров
          Арг:
            prices(list) - список из цен товаров
            client_id - переменная из окружения
            seller_token - АПИ токен для доступа к АПИ сайта
            
          Возвращает:
            response.json() - dict c обновленной ценой

          Пример: 
            {}            
    """
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"prices": prices}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def update_stocks(stocks: list, client_id, seller_token):
    """Обновляет остатки
          Арг:
            stocks(list) - список из цен товаров
            client_id - переменная из окружения
            seller_token - АПИ токен для доступа к АПИ сайта
            
          Возвращает:
            response.json() - dict c обновленными остатками

          Пример: 
            {} 
    """
    url = "https://api-seller.ozon.ru/v1/product/import/stocks"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"stocks": stocks}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def download_stock():
    """Скачать файл ostatki с сайта casio
            
          Возвращает:
            словарь с позициями и количеством остатков товара на сайте

    """
    # Скачать остатки с сайта
    casio_url = "https://timeworld.ru/upload/files/ostatki.zip"
    session = requests.Session()
    response = session.get(casio_url)
    response.raise_for_status()
    with response, zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(".")
    # Создаем список остатков часов:
    excel_file = "ostatki.xls"
    watch_remnants = pd.read_excel(
        io=excel_file,
        na_values=None,
        keep_default_na=False,
        header=17,
    ).to_dict(orient="records")
    os.remove("./ostatki.xls")  # Удалить файл
    return watch_remnants

def create_stocks(watch_remnants, offer_ids):
    # Уберем то, что не загружено в seller
  """Создает словарь с остатками
  
          Арг:
            watch_remnants - dict с количеством остатков на сайте
            offer_ids - list Список из артикулов товаров
            
          Возвращает:
            stocks - dict с артикулом(offer_id) товара и остатками(watch.get("Код"))

          Пример: 
            {1223253: 25} 
  """
    stocks = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append({"offer_id": str(watch.get("Код")), "stock": stock})
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append({"offer_id": offer_id, "stock": 0})
    return stocks

def create_prices(watch_remnants, offer_ids):
    """Собирает цены товаров
  
          Арг:
            watch_remnants - dict с количеством остатков на сайте
            offer_ids - list Список из артикулов товаров
            
          Возвращает:
            prices - dict с валютой (currency_code), артикулом(offer_id) и ценой товара (price)

          Пример: 
           price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": 122343),
                "old_price": "0",
                "price": 5999),
            }
    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": str(watch.get("Код")),
                "old_price": "0",
                "price": price_conversion(watch.get("Цена")),
            }
            prices.append(price)
    return prices
  
def price_conversion(price: str) -> str:
"""
    Преобразовать цену.

    Арг:
        Параметр 1: price в формате str '5'990.00 руб'
    
        Возвращает: Преобразованный параметр в строку формата 5990

        Пример корректный: 5'990.00 руб. -> 5990

        Пример некорректный: 5'990.00 руб. -> 5'990
"""
    return re.sub("[^0-9]", "", price.split(".")[0])

def divide(lst: list, n: int):
    """Делит список lst на части по n элементов
          Арг:
            list - список элементов
            n - int количество на которое надо разбить список
            
          yield:
            n количество частей списка 

          Пример: 
           lst = [1,2,3,4,5,6,7,8]

            for i in range(0, len(lst), 4):
                lst1 = lst[i : i+4]
                print(lst1)  
                
            [1, 2, 3, 4]
            [5, 6, 7, 8]
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def upload_prices(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_price in list(divide(prices, 1000)):
        update_price(some_price, client_id, seller_token)
    return prices


async def upload_stocks(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    stocks = create_stocks(watch_remnants, offer_ids)
    for some_stock in list(divide(stocks, 100)):
        update_stocks(some_stock, client_id, seller_token)
    not_empty = list(filter(lambda stock: (stock.get("stock") != 0), stocks))
    return not_empty, stocks


def main():
    env = Env()
    seller_token = env.str("SELLER_TOKEN")
    client_id = env.str("CLIENT_ID")
    try:
        offer_ids = get_offer_ids(client_id, seller_token)
        watch_remnants = download_stock()
        # Обновить остатки
        stocks = create_stocks(watch_remnants, offer_ids)
        for some_stock in list(divide(stocks, 100)):
            update_stocks(some_stock, client_id, seller_token)
        # Поменять цены
        prices = create_prices(watch_remnants, offer_ids)
        for some_price in list(divide(prices, 900)):
            update_price(some_price, client_id, seller_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
