import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid(url, base_url):
    """ Check if the URL is a valid internal link """
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == urlparse(base_url).netloc

def crawl_site(base_url, file_path):
    visited = set()
    urls = set()
    urls.add(base_url)
    
    with open(file_path, 'w') as file:
        while urls:
            url = urls.pop()
            if url not in visited:
                visited.add(url)
                file.write(url + '\n')
                file.flush()  # Ensures that each URL is written to the file immediately
                try:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        full_url = urljoin(url, link['href'])
                        if full_url not in visited and is_valid(full_url, base_url):
                            urls.add(full_url)
                except requests.RequestException:
                    continue

# Base URL of the site to crawl
base_url = 'https://community.openstreetmap.org/'

# File path to save the URLs
file_path = 'sitemap.txt'

# Start crawling from the base URL
crawl_site(base_url, file_path)

print("Sitemap has been generated and saved to sitemap.txt.")
