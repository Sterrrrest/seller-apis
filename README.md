Что делает скрипт?
=
seller.py
=

Скрипт  получает список по артикулам товаров с сайта, сравнивает их с товарами на маркетплейсе. 
Создает список оставшихся товаров и загружает их на маркетплейс. Далее обновляет цены в соответсвии с ценами на сайте.

Запуск
-
- Для запуска необходим ключ API к маркетплейсу OZON. 
- Необходим идентификатор клиента.

market.py
=

Скрипт получает список на сайте и затем заливате их в магазины FBS и DBS на Яндекс маркете. Оновляет цен в соответствии с сайтом.

Запуск
-
- Для запуска необходим ключ API к маркетплейсу OZON. 
- Необходим идентификатор FBS компании.
- Необходим идентификатор DBS компании.
- (warehouse)Идентификатор склада FBS.
- (warehouse)Идентификатор склада DBS.
