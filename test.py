from wiki_crawler import crawl_wiki
import sqlite3
from collections import Counter

start_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
db_name = 'test_db'
depth = 1

with sqlite3.connect(db_name) as conn:
    conn.execute("DELETE FROM links")
    conn.commit()
crawl_wiki(start_url, db_name, depth)
with sqlite3.connect(db_name) as conn:
            cursor = conn.execute('SELECT url FROM links')
            urls = [row[0] for row in cursor.fetchall()]
            print(urls)
            print(len(urls))
            c = Counter(urls)
            for i in range(len(urls)):
                if c[urls[i]] > 1:
                    print("1")
                    break
            
            cursor.execute("DELETE FROM links")
            conn.commit()

