# PRINT THE ANIME LINKS OF ALL THE PROFILES
# CAN BE RATE LIMITED SO BE AWARE
# I DON'T STEAL I MAKE THEM MORE ACCESSIBLE FOR EVERYONE

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url, max_pages):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    urls = set()
    videos = set()
    domain_name = urlparse(url).netloc
    page = 1
    retry_delay = 1
    max_retries = 5

    while True:
        print(f"Checking page {page} of {url}...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429:
                print(f"Rate limited! Waiting for {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
                if retry_delay > 60:
                    retry_delay = 60
                retries_left = max_retries - 1
                if retries_left == 0:
                    print("Max retries exceeded. Giving up.")
                    break
                continue
            else:
                raise

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                continue
            if href in urls:
                continue
            if domain_name not in href:
                continue
            print(f"\033[42m \033[0m {href}")
            urls.add(href)

            if href.startswith("https://video.sibnet.ru/video"):
                videos.add(href)
                print(f"Found video: {href}")

        print(f"Videos found on page {page}:")
        for video in videos:
            print(video)

        if page == max_pages:
            break
        next_page_url = url.replace(f"?page={page}", f"?page={page + 1}")
        response = requests.head(next_page_url)
        if response.status_code == 404:
            break
        url = next_page_url
        page += 1
        retry_delay = 1

    return urls, videos

if __name__ == "__main__":
    urls_to_crawl = [
        {"url": "https://video.sibnet.ru/users/Adel%20Lmt/favorite/other/?page=1", "max_pages": 14},
        {"url": "https://video.sibnet.ru/users/Matrixx%20Xenos/favorite/other/?page=1", "max_pages": 11},
        {"url": "https://video.sibnet.ru/pls682500/&page=1", "max_pages": 8},
    ]

    for url_info in urls_to_crawl:
        print(f"Crawling {url_info['url']}...")
        urls, videos = get_all_website_links(url_info["url"], url_info["max_pages"])
        print(f"Found {len(videos)} videos:")
        for video in videos:
            print(video)
        print("Done!")
