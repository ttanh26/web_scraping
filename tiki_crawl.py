from bs4 import BeautifulSoup
import selenium
import requests
import sqlite3
import pandas as pd
import re

#BASE URL
TIKI_URL = 'https://tiki.vn/'

#Create database about category
conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

#Create table in database
def create_product_table():
    query = '''
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id VARCHAR(255),
                seller_id VARCHAR(255),
                name VARCHAR(255),
                url TEXT,
                price INTEGER,
                cat_id INTEGER,
                FOREIGN KEY (cat_id) REFERENCES categories (id)
            )
            '''
    
    try:
        cur.execute('DROP TABLE products')
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)
    
    cur.execute(query)

def create_category_table():
    query = '''
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255),
                url TEXT,
                parent_id INTEGER,
                create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
    
    try:
        cur.execute('DROP TABLE categories')
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)
        
    cur.execute(query)

# Create a class product with 5 attributes: product_id, seller_id, name, url, price, cat_id and 1 method: save_db()
class Item():
    def __init__(self, product_id, seller_id, name, url, price, cat_id):
        self.product_id = product_id
        self.seller_id = seller_id
        self.name = name
        self.url = url
        self.price = price
        self.cat_id = cat_id

    def __repr__(self):
        return f'Product ID: {self.product_id}, Seller: {self.seller_id}, Name: {self.name}, Price: {self.price}, URL: {self.url} \n'

    def save_db(self):
        query = '''
                INSERT INTO products (product_id, seller_id, name, price, url, cat_id)
                VALUES (?, ?, ?, ?, ?, ?)
                '''
        
        val = (self.product_id, self.seller_id, self.name, self.price, self.url, self.cat_id)

        try:
            cur.execute(query, val)
        except Exception as err:
            print('ERROR AT INSERT ROW INTO products', err, self.product_id, self.name)
        
# Create a category class with 4 attributes: name, url, parent_id, cat_id and 1 methods: save_db()
class Category():
    def __init__(self, name, url, parent_id = None, cat_id = None):
        self.name = name
        self.url = url
        self.parent_id = parent_id
        self.cat_id = cat_id

    def __repr__(self):
        return f'ID: {self.cat_id}, Name: {self.name}, URL: {self.url}, parent_id: {self.parent_id} \n'

    def save_db(self):
        query = '''
                INSERT INTO categories (name, url, parent_id)
                VALUES (?, ?, ?)
                '''

        val = (self.name, self.url, self.parent_id)

        try:
            cur.execute(query, val)
        except Exception as err:
            print('ERROR AT INSERT ROW INTO categories', err, self.name)

# Get the html source code:
def get_url(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    return soup
    
# Get the main categories of Tiki
def get_main_categories(url):
    l = []
    try:
        soup = get_url(url)

        for main_cat in soup.find_all('li', {'class': 'MenuItem-sc-181aa19-0'}):
            name = main_cat.a.find('span', {'class': 'text'}).text
            url = main_cat.a['href']
            main_cat = Category(name, url)
            main_cat.save_db()
            l.append(main_cat)
    except Exception as err:
        print('ERROR AT MAIN CATEGORIES', err)

    return (l, None)

# Get the sub categories
def get_sub_categories(parent_cat):
    url = parent_cat.url
    l = []
    
    try:
        soup = get_url(url)

        for sub_cat in soup.find_all('div', {'class': 'list-group-item is-child'}):
            name = re.sub(r'\s{2,}', ' ', sub_cat.a.text)
            url = TIKI_URL + sub_cat.a['href']
            sub = Category(name, url, parent_id = parent_cat.cat_id)
            sub.save_db()
            l.append(sub)
    except Exception as err:
        print('ERROR AT SUB CATEGOGRIES', err, sub_cat.name, parent_cat.name)
    
    s = (l, parent_cat)
    return s

# Get the product list of a lowest-level category
def get_product(cat):
    k = 1
    l = []

    try:
        soup = get_url(cat.url)
        product_list = soup.find_all('div', {'class': 'product-item'})

        while product_list != []:
            for p in product_list:
                p_id = p['data-id']
                s_id = p['data-seller-product-id']
                name = p['data-title']
                url = p.a['href']
                price = p['data-price']
                cat_id = cat.cat_id
                item = Item(p_id, s_id, name, url, price, cat_id)
                item.save_db()
                l.append(item)
            
            k += 1
            url = cat.url + '&page=' + str(k)
            soup = get_url(url)
            product_list = soup.find_all('div', {'class': 'product-item'})
    except Exception as err:
        print('ERROR BY GETTING ITEM', err, cat.name)

    return l

# Get all the sub-categories
def get_all_categories(cat):
    if len(cat[0]) == 0:
        get_product(cat[1])

    for m in cat[0]:
        sub = get_sub_categories(m)
        get_all_categories(sub)


if __name__ == "__main__":
#     create_category_table()
    create_product_table()
#     main = get_main_categories(TIKI_URL)
    
#     c = get_sub_categories(main[0][8])
#     d = get_all_categories(c)
#     print(d)


    

