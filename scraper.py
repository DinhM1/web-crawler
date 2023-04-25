import re
import posixpath

from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, SoupStrainer

from nltk.tokenize import RegexpTokenizer


def scraper(url, resp):
    links = extract_next_links(url, resp)
    tokens = tokenize(resp)

    return [link for link in links if is_valid(link)], tokens


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    links = []

    count = 0

    if resp.status == 200 and is_valid(url):
        soup = BeautifulSoup(resp.raw_response.content, "lxml")

        for element in soup.findAll('a'):
            if len(element.get('href')) < 2:
                pass
            elif element.get('href').startswith("#"):
                pass
            elif element.get('href').startswith("//"):
                proper_url = element.get('href').split("//")[1]
                links.append(proper_url)
                count = count + 1
            elif element.get('href').startswith("/"):
                absolute_url = urljoin(url, element.get('href'))
                links.append(absolute_url)
                count = count + 1
            elif is_valid(element.get('href')):
                count = count + 1
            else:
                fixed_url = urljoin(url, "/" + element.get('href'))

    return links

def tokenize(response):
    soup = BeautifulSoup(response.raw_response.content, "lxml")
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(soup.get_text())

    return tokens


def process_relative(url):
    if url.startswith("www."):
        return "https://" + url
    else:
        return "https://www." + url


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
