import unittest
from unittest.mock import patch, MagicMock
from wiki_crawler import fetch_page, parse_links_from_wiki_page, create_database, save_link, crawl_wiki
import sqlite3
from multiprocessing import Pool, Manager # Импорт необходимых библиотек


# Класс для тестирования функций в wiki_crawler
class TestWikiCrawler(unittest.TestCase):
    @patch('http.client.HTTPSConnection') # Мокаем HTTPSConnection для тестирования
    def test_fetch_page(self, mock_https):
        # Создаем мок-ответ для успешного запроса
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'<html></html>' # Возвращаемый HTML-контент
        mock_https.return_value.getresponse.return_value = mock_response # Настраиваем мок
        
        result = fetch_page('https://en.wikipedia.org/wiki/Python_(programming_language)') # Вызываем тестируемую функцию
        self.assertEqual(result, '<html></html>') # Проверяем, что результат соответствует ожидаемому

    @patch('http.client.HTTPSConnection')
    def test_parse_links_from_wiki_page(self, mock_https):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'<a href="/wiki/Link1">Link1</a><a href="/wiki/Link2">Link2</a>'
        mock_https.return_value.getresponse.return_value = mock_response
        
        links = parse_links_from_wiki_page('https://en.wikipedia.org/wiki/Python_(programming_language)') # Вызываем тестируемую функцию
        self.assertIn('https://en.wikipedia.org/wiki/Link1', links)  # Проверяем, что ссылки были правильно распознаны
        self.assertIn('https://en.wikipedia.org/wiki/Link2', links)  # Проверяем, что ссылки были правильно распознаны

    def test_save_link(self):
        db_name = 'test.db' # Имя тестовой базы данных
        create_database(db_name) # Создаем базу данных
        save_link(db_name, 'https://en.wikipedia.org/wiki/Python_(programming_language)')  # Сохраняем ссылку

        # Проверяем, что ссылка была успешно сохранена в базе данных
        with sqlite3.connect(db_name) as conn:
            cursor = conn.execute('SELECT url FROM links')
            urls = [row[0] for row in cursor.fetchall()] # Извлекаем все ссылки
            self.assertIn('https://en.wikipedia.org/wiki/Python_(programming_language)', urls) # Проверяем наличие ссылки

    def test_crawl_wiki(self):
        start_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'  # Начальный URL для обхода
        db_name = 'test_db' # Имя тестовой базы данных
        depth = 2 # Глубина обхода
    

        create_database(db_name)  # Создаем базу данных

        # Очищаем таблицу перед тестом
        with sqlite3.connect(db_name) as conn:
            conn.execute("DELETE FROM links")
            conn.commit()
        
        
        crawl_wiki(start_url, db_name, depth) # Запускаем функцию обхода

        urls = [] # Список для хранения извлеченных URL


        with sqlite3.connect(db_name) as conn:
            # Извлечение всех ссылок из базы данных 
            cursor = conn.execute('SELECT url FROM links')
            urls = [row[0] for row in cursor.fetchall()]

        self.assertEqual(56204, len(urls), "Числа не равны") # Проверка количества сохраненных ссылок

if __name__ == '__main__':

    unittest.main() # Запуск тестов

