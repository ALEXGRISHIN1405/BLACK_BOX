import unittest
from unittest.mock import patch, MagicMock
from wiki_crawler import fetch_page, parse_links_from_wiki_page, create_database, save_link, crawl_wiki
import sqlite3
from multiprocessing import Pool, Manager

class TestWikiCrawler(unittest.TestCase):
    @patch('http.client.HTTPSConnection')
    def test_fetch_page(self, mock_https):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'<html></html>'
        mock_https.return_value.getresponse.return_value = mock_response
        
        result = fetch_page('https://en.wikipedia.org/wiki/Python_(programming_language)')
        self.assertEqual(result, '<html></html>')

    @patch('http.client.HTTPSConnection')
    def test_parse_links_from_wiki_page(self, mock_https):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'<a href="/wiki/Link1">Link1</a><a href="/wiki/Link2">Link2</a>'
        mock_https.return_value.getresponse.return_value = mock_response
        
        links = parse_links_from_wiki_page('https://en.wikipedia.org/wiki/Python_(programming_language)')
        self.assertIn('https://en.wikipedia.org/wiki/Link1', links)
        self.assertIn('https://en.wikipedia.org/wiki/Link2', links)

    def test_save_link(self):
        db_name = 'test.db'
        create_database(db_name)
        save_link(db_name, 'https://en.wikipedia.org/wiki/Python_(programming_language)')
        with sqlite3.connect(db_name) as conn:
            cursor = conn.execute('SELECT url FROM links')
            urls = [row[0] for row in cursor.fetchall()]
            self.assertIn('https://en.wikipedia.org/wiki/Python_(programming_language)', urls)

    def test_crawl_wiki(self):
        start_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
        db_name = 'test_db'
        depth = 2
    

        create_database(db_name)

        with sqlite3.connect(db_name) as conn:
            conn.execute("DELETE FROM links")
            conn.commit()
        
        
        crawl_wiki(start_url, db_name, depth)

        urls = []

        with sqlite3.connect(db_name) as conn:
            cursor = conn.execute('SELECT url FROM links')
            urls = [row[0] for row in cursor.fetchall()]
            print(urls)


if __name__ == '__main__':

    unittest.main()

