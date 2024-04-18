import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sqlite3

def setup_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            url TEXT PRIMARY KEY,
            visited INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_url_to_database(url, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', (url,))
    conn.commit()
    conn.close()

def mark_url_as_visited(url, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE urls SET visited = 1 WHERE url = ?', (url,))
    conn.commit()
    conn.close()

def get_next_url(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT url FROM urls WHERE visited = 0 LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def is_valid(url, base_url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == urlparse(base_url).netloc

def crawl_site(base_url, db_path):
    setup_database(db_path)
    add_url_to_database(base_url, db_path)
    url = get_next_url(db_path)

    while url:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            mark_url_as_visited(url, db_path)

            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if is_valid(full_url, base_url):
                    add_url_to_database(full_url, db_path)

        except requests.RequestException:
            mark_url_as_visited(url, db_path)  # Mark as visited even if failed to ensure progress

        url = get_next_url(db_path)

# Base URL of the site to crawl
base_url = 'https://community.openstreetmap.org/'

# SQLite database file path
db_path = 'urls.db'

# Start crawling from the base URL
crawl_site(base_url, db_path)

print("Crawling has completed or paused. Data saved in database.")
