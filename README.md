offer_ids - список  нужных id товаров с сайта Озон. переменная, которая принимает занчение функции get_offer_ids с нужными доступами, в нащем случае id клиента и токен доступа. 
get_product_list
watch_remnants - переменная, которая содержит список с остатками часов Casio. Содержит функцию download_stock , которая возвращает словарь watch_remnants
stocks - переменная, которая принимет значение функции create_stocks, на входе у нее словарь watch_remnants и offer_ids. 
Сравнивает список остатков на сайте и озоне и заносит остатки в словарь stocks

Загружает stocks на сайт Озон

Меняет цены функция create_prices. Возвращает цену prices в формате "9999"

Что делает скрипт?
=
Скрипт seller.py получает список по артикулам товаров с сайта и сравнивает их с товарами на маркетплейсе. 
Создает список оставшихся товаров и загружает их на маркетплейс. Далее обновляет цены в соответсвии с ценами на сайте.
