from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger

import scraper
import time
import re


class Results:
    def __init__(self):
        self.unique_pages = set()
        self.longest_page_count = 0
        self.words = {}
        self.subdomains = {}

    def add_unique_page(self, url):
        self.unique_pages.add(url)

    def update_page_count(self, count):
        if count > self.longest_page_count:
            self.longest_page_count = count

    def add_word(self, word):
        if word in self.words:
            self.words[word] = self.words[word] + 1
        else:
            self.words[word] = 1

    def add_subdomain(self, url):
        subdomain_pattern = r'^(?:https?://)?([a-zA-Z0-9-]+\.)*(ics\.uci\.edu)(?:/|$)'
        match = re.match(subdomain_pattern, url)
        subdomain = match.group(1) if match else None
        print(subdomain)

        if subdomain in self.subdomains:
            self.subdomains[subdomain] = self.subdomains[subdomain] + 1
        else:
            self.subdomains[subdomain] = 1


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {
            -1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {
            -1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        results = Results()

        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
