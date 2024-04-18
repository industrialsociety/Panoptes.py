import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sqlite3
import sys
import time
import threading
import msvcrt

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

def get_stats(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM urls WHERE visited = 1')
    visited_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM urls')
    total_count = cursor.fetchone()[0]
    conn.close()
    return visited_count, total_count

def is_valid(url, base_url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == urlparse(base_url).netloc

def status_reporter(db_path):
    while True:
        if msvcrt.kbhit() and msvcrt.getch() == b's':
            visited_count, total_count = get_stats(db_path)
            print(f'Status Update: Total URLs: {total_count}, Visited URLs: {visited_count}')
        time.sleep(0.1)  # Sleep briefly to prevent this loop from consuming too much CPU.

def crawl_site(base_url, db_path):
    setup_database(db_path)
    add_url_to_database(base_url, db_path)
    url = get_next_url(db_path)
    
    # Start status reporter thread
    status_thread = threading.Thread(target=status_reporter, args=(db_path,))
    status_thread.daemon = True
    status_thread.start()

    try:
        while url:
            try:
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'lxml')
                mark_url_as_visited(url, db_path)

                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    if is_valid(full_url, base_url):
                        add_url_to_database(full_url, db_path)

            except requests.RequestException as e:
                print(f'Failed to fetch {url}: {e}')
                mark_url_as_visited(url, db_path)

            url = get_next_url(db_path)
    except KeyboardInterrupt:
        print('Script interrupted by user. Exiting...')
        sys.exit(0)

# Base URL of the site to crawl
base_url = 'example.com'

# SQLite database file path
db_path = 'urls.db'

# Start crawling from the base URL
crawl_site(base_url, db_path)

print('Crawling has completed or paused. Data saved in database.')
