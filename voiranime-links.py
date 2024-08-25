# BE AWARE THERE IS A LOTS OF LINKS
# MORE THAN 50K

import requests
import concurrent.futures
from lxml import etree
import threading
import json
import os

print_lock = threading.Lock()
urls_file = 'urls.json'

def crawl_sitemap_index(url):
    response = requests.get(url)
    root = etree.fromstring(response.content)

    sitemap_urls = []
    for elem in root:
        if elem.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap':
            sitemap_url = elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            sitemap_urls.append(sitemap_url)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(crawl_sitemap, sitemap_urls)

def crawl_sitemap(url):
    response = requests.get(url)
    root = etree.fromstring(response.content)

    urls = []
    for elem in root:
        if elem.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}url':
            url_loc = elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            urls.append(url_loc)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(search_url, urls)

def search_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        with print_lock:
            print_url(url)

def print_url(url):
    with open(urls_file, 'r+') as f:
        urls = json.load(f)
        if url in urls:
            print(f"\033[91m{url}\033[0m")
        else:
            print(f"\033[92m{url}\033[0m")
            urls.append(url)
            f.seek(0)
            json.dump(urls, f, indent=4)
            f.truncate()

if __name__ == '__main__':
    if not os.path.exists(urls_file):
        with open(urls_file, 'w') as f:
            json.dump([], f)

    sitemap_index_url = 'https://v5.voiranime.com/sitemap_index.xml'
    crawl_sitemap_index(sitemap_index_url)
