from threading import Thread
from inspect import getsource
from utils.download import download
from utils import get_logger

import scraper
import time
import re
import tldextract


class Results:
    def __init__(self):
        self.unique_pages = set()
        self.longest_page_count = 0
        self.words = {}
        self.subdomains = {}
        self.stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours	ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]

    def add_subdomain(self, url):
        # extract = tldextract.extract(url)
        # print(extract)
        # subdomain = extract.subdomain

        subdomain_pattern = r'^(?:https?://)?([a-zA-Z0-9-]+\.)*?ics\.uci\.edu'
        match = re.match(subdomain_pattern, url)
        subdomain = match.group(1) if match else None
        print(subdomain)

        if subdomain in self.subdomains:
            self.subdomains[subdomain] = self.subdomains[subdomain] + 1
        else:
            self.subdomains[subdomain] = 1

    def add_unique_page(self, url):
        self.unique_pages.add(url.split("#")[0])
        self.add_subdomain(url)

    def update_longest_length(self, count):
        if count > self.longest_page_count:
            self.longest_page_count = count

    def print_longest_length(self):
        print(self.longest_page_count)

    def add_word(self, new_word):
        word = new_word.lower()
        if word not in self.stopwords:
            if word in self.words:
                self.words[word] = self.words[word] + 1
            else:
                self.words[word] = 1

    def get_words(self):
        sorted_dict = sorted(self.words.items(), key=lambda x: x[1], reverse=True)

        for entry in sorted_dict:
            print(entry[0] + " -> " + str(entry[1]))

    def get_subdomains(self):
        print(len(self.subdomains.keys()))
        for subdomain in self.subdomains.keys():
            print(subdomain + " -> " + str(self.subdomains[subdomain]))


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

            scraped_urls, tokens = scraper.scraper(tbd_url, resp)

            for token in tokens:
                results.add_word(token)

            results.update_longest_length(len(tokens))

            for scraped_url in scraped_urls:
                results.add_unique_page(scraped_url)
                if scraped_url not in results.unique_pages:
                    self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        # results.get_words()
        # results.print_longest_length()
        results.get_subdomains()

