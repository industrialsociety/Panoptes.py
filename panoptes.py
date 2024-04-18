import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid(url, base_url):
    """ Check if the URL is a valid internal link """
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == urlparse(base_url).netloc

def crawl_site(base_url):
    visited = set()
    urls = set()
    urls.add(base_url)
    
    while urls:
        url = urls.pop()
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if full_url not in visited and is_valid(full_url, base_url):
                    visited.add(full_url)
                    urls.add(full_url)
                    print(full_url)  # Optional: prints the URL to the console
        except requests.RequestException:
            continue
    
    return visited

def save_urls_to_file(urls, file_path):
    with open(file_path, 'w') as file:
        for url in sorted(urls):
            file.write(url + '\n')

# Base URL of the site to crawl
base_url = 'example.com'

# Start crawling from the base URL and get all encountered URLs
crawled_urls = crawl_site(base_url)

# Save the URLs to a text file
save_urls_to_file(crawled_urls, 'sitemap.txt')

print("Sitemap has been generated and saved to sitemap.txt.")
