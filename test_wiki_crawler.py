import unittest
from unittest.mock import patch, MagicMock
from wiki_crawler import fetch_page, parse_links_from_wiki_page, create_database, save_link
import sqlite3

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

if __name__ == '__main__':
    unittest.main()

