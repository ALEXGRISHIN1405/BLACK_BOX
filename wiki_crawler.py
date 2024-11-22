import sqlite3
import http.client
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser
from typing import List, Set, Tuple, Optional

class WikiLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: Set[str] = set()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    href = attr[1]
                    if href.startswith('/wiki/') and ':' not in href:
                        self.links.add(urljoin('https://en.wikipedia.org', href))

def create_database(db_name: str) -> None:
    with sqlite3.connect(db_name) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS links (url TEXT PRIMARY KEY)')

def save_link(db_name: str, url: str) -> None:
    with sqlite3.connect(db_name) as conn:
        conn.execute('INSERT OR IGNORE INTO links (url) VALUES (?)', (url,))

def save_links(db_name: str, visited: Set[str]) -> None:
    with sqlite3.connect(db_name) as conn:
        for url in visited:
            conn.execute('INSERT OR IGNORE INTO links (url) VALUES (?)', (url,))
        conn.commit()

def fetch_page(url: str) -> Optional[str]:
    parsed_url = urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    try:
        conn.request("GET", parsed_url.path)
        response = conn.getresponse()
        if response.status == 200:
            return response.read().decode('utf-8')
        return None
    finally:
        conn.close()

def parse_links_from_wiki_page(url: str) -> Set[str]:
    html_content = fetch_page(url)
    if html_content is None:
        return set()
    parser = WikiLinkParser()
    parser.feed(html_content)
    return parser.links

def crawl_wiki(start_url: str, db_name: str, depth: int) -> None:
    visited: Set[str] = set()
    to_visit: List[Tuple[str, int]] = [(start_url, 0)]
    create_database(db_name)
    while to_visit:
        current_url, current_depth = to_visit.pop(0)
        if current_depth <= depth:
            if current_url not in visited:
                visited.add(current_url)
                to_visit = accept_to_parse(current_depth, depth, to_visit, current_url, visited)        
        else:
            break
    save_links(db_name, visited)

def accept_to_parse(current_depth: int, depth: int, to_visit: List[Tuple[str, int]], current_url: str, visited: Set[str]) -> List[Tuple[str, int]]:
    if current_depth < depth:
        links = parse_links_from_wiki_page(current_url)
        for link in links:
            to_visit.append((link, current_depth + 1))
    return to_visit

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Crawl Wikipedia for links.')
    parser.add_argument('url', type=str, help='The starting Wikipedia article URL')
    parser.add_argument('--db', type=str, default='wiki_links.db', help='Database name')
    parser.add_argument('--depth', type=int, default=6, help='Depth of crawling')
    args = parser.parse_args()

    create_database(args.db)
    crawl_wiki(args.url, args.db, args.depth)
