import sqlite3
import http.client
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser
from typing import List, Set, Tuple, Optional
import argparse # Импорт необходимых библиотек

# Класс для парсинга ссылок на страницы Википедии
class WikiLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: Set[str] = set() # Множество для хранения уникальных ссылок

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        # Обрабатываем начальные теги
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    href = attr[1]
                    # Проверяем, что ссылка ведет на статью Википедии
                    if href.startswith('/wiki/') and ':' not in href:
                        self.links.add(urljoin('https://en.wikipedia.org', href)) # Добавляем полную ссылку

# Функция для создания базы данных
def create_database(db_name: str) -> None:
    with sqlite3.connect(db_name) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS links (url TEXT PRIMARY KEY)') # Создаем таблицу для хранения ссылок, если она не существует


# Функция для сохранения ссылки в базу данных
def save_link(db_name: str, url: str) -> None:
    with sqlite3.connect(db_name) as conn:
        conn.execute('INSERT OR IGNORE INTO links (url) VALUES (?)', (url,)) # Вставляем ссылку, если она еще не существует


# Функция для сохранения ссылок в базу данных
def save_links(db_name: str, visited: Set[str]) -> None:
    with sqlite3.connect(db_name) as conn:
        for url in visited:
            conn.execute('INSERT OR IGNORE INTO links (url) VALUES (?)', (url,)) # Вставляем ссылки, которых не существует
        conn.commit()


# Функция для получения HTML-контента страницы по URL
def fetch_page(url: str) -> Optional[str]:
    parsed_url = urlparse(url) # Функция для получения HTML-контента страницы по URL
    conn = http.client.HTTPSConnection(parsed_url.netloc) # Устанавливаем HTTPS-соединение
    try:
        conn.request("GET", parsed_url.path) # Отправляем GET-запрос
        response = conn.getresponse() # Получаем ответ
        if response.status == 200:
            return response.read().decode('utf-8') # Возвращаем содержимое страницы в виде строки
        return None#  Если статус не 200, возвращаем None
    finally:
        conn.close()


# Функция для парсинга ссылок со страницы Википедии
def parse_links_from_wiki_page(url: str) -> Set[str]:
    html_content = fetch_page(url) # Получаем HTML-контент страницы
    if html_content is None:
        return set() # Если контент не получен, возвращаем пустое множество
    parser = WikiLinkParser() # Создаем экземпляр парсера
    parser.feed(html_content) # Парсим HTML-контент
    return parser.links # Возвращаем найденные ссылки


# Основная функция для обхода Википедии
def crawl_wiki(start_url: str, db_name: str, depth: int) -> None:
    visited: Set[str] = set() # Множество для хранения посещенных ссылок
    to_visit: List[Tuple[str, int]] = [(start_url, 0)] # Список для хранения ссылок для посещения и их глубины
    create_database(db_name) # Создаем базу данных
    while to_visit:
        current_url, current_depth = to_visit.pop(0) # Извлекаем первую ссылку
        if current_depth <= depth:
            if current_url not in visited:
                visited.add(current_url) # Добавляем ссылку в посещенные
                to_visit = accept_to_parse(current_depth, depth, to_visit, current_url, visited) # Обрабатываем ссылки    
        else:
            break # Если достигли максимальной глубины, выходим из цикла
    save_links(db_name, visited) # Сохраняем ссылки в базу данных


# Функция для добавления ссылок для парсинга
def accept_to_parse(current_depth: int, depth: int, to_visit: List[Tuple[str, int]], current_url: str, visited: Set[str]) -> List[Tuple[str, int]]:
    if current_depth < depth:
        links = parse_links_from_wiki_page(current_url) # Получаем ссылки со страницы
        for link in links:
            to_visit.append((link, current_depth + 1)) # Добавляем ссылку в список для посещения с увеличенной глубиной
    return to_visit # Возвращаем обновленный список ссылок для посещения

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Crawl Wikipedia for links.')  # Создаем парсер аргументов
    parser.add_argument('url', type=str, help='The starting Wikipedia article URL') # Аргумент для начального URL
    parser.add_argument('--db', type=str, default='wiki_links.db', help='Database name') # Аргумент для имени базы данных
    parser.add_argument('--depth', type=int, default=6, help='Depth of crawling') # Аргумент для глубины обхода
    args = parser.parse_args() # Парсим аргументы командной строки

    create_database(args.db) # Создаем базу данных
    crawl_wiki(args.url, args.db, args.depth) # Запускаем обход Википедии с заданными параметрами
