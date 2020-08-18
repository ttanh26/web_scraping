#%%
import sqlite3
from tiki_crawl import *

# conn = sqlite3.connect('tiki.db')
# cur = conn.cursor()

# print(cur.execute('SELECT COUNT(*) FROM categories').fetchall())
# %%
create_category_table()
create_product_table()
main = get_main_categories(TIKI_URL)
# %%
