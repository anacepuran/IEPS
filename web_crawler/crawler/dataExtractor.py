from db.db import *
import time
import urlcanon
from urllib.parse import urljoin
from crawler.duplicateDetector import *
from urllib.parse import urlparse
from crawler.robots import *

'''
When your crawler fetches and renders a web page, do some simple parsing to detect images and next links.
When parsing links, include links from href attributes and onclick Javascript events (e.g. location.href or document.location).
Be careful to correctly extend the relative URLs before adding them to the frontier.
Detect images on a web page only based on img tag, where the src attribute points to an image URL.
Donwload HTML content only. List all other content (.pdf, .doc, .docx, .ppt and .pptx) in the page_data table - there is no need to populate
data field (i.e. binary content). In case you put a link into a frontier and identify content as a binary source,
you can just set its page_type to BINARY. The same holds for the image data.
'''


DOMAIN = '.gov.si'
BINARY_CONTENT = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
IMAGE_CONTENT = [".png", ".jpg", ".jpeg", ".gif"]
IGNORE_SEED_URLS = ['evem.gov.si', 'e-uprava.gov.si',
                    'e-prostor.gov.si', 'euprava.gov.si', 'eprostor.gov.si']
IGNORE_DOMAIN_VARIATIONS = ('.gov.si', 'gov.si', 'www.gov.si')
PATH_EXCLUSIONS = ["favicon.ico", "data:image", "base64",
                   "maps.googleapis.", "maps.gstatic", "fonts.googleapis.", ".css", ".zip"]
EXTRAS = ["https://www.", "http://www.",
          "https://", "http://", ".html", "www.", "www"]


def fetchData(html_content, current_page, db_connection):
    images = binary = urls = disallowed_rules = []
    current_page_url = current_page[3]

    print("Current page URL: ", current_page_url)
    seed_site_data = getSeedSiteFromDB(current_page, db_connection)

    # RESPECT THE CRAWL DELAY
    if seed_site_data is not None:
        crawl_delay = seed_site_data[4]
        if crawl_delay is not None:
            time.sleep(crawl_delay)
        # GET DISALLOWED RULES
        robots_file = seed_site_data[2]
        if robots_file is not None:
            disallowed_rules = getDisallowedFromRobotsFile(robots_file)

    # GET IMG LINKS
    for link in html_content.find_all("img"):
        image_url = getImageLinks(current_page_url, disallowed_rules, link)
        if image_url is not None:
            insertImageData(image_url, current_page, db_connection)

    # GET HREF LINKS
    for link in html_content.find_all(href=True):
        href_url = getNonImageLinks(
            current_page_url, link, "href", disallowed_rules, db_connection)
        if href_url is not None:
            if href_url[0] == "IMAGE":
                insertImageData(href_url[1], current_page, db_connection)
            else:
                handleNonImageSite(href_url[1], current_page, db_connection)

    # GET ONCLICK LINKS
    for link in html_content.find_all(onclick=True):
        onclick_url = getNonImageLinks(
            current_page_url, link, "onclick", disallowed_rules, db_connection)
        if onclick_url is not None:
            if onclick_url[0] == "IMAGE":
                insertImageData(onclick_url[1], current_page, db_connection)
            else:
                handleNonImageSite(onclick_url[1], current_page, db_connection)


def getImageLinks(current_page_url, disallowed_rules, link):
    src = link['src']
    if src is not None and len(src) != 0:
        # apply disallowed rules
        for rule in disallowed_rules:
            if rule in src:
                return None
        '''
        if current_page_url not in src:
            src = urljoin("http://" + current_page_url, src)
        '''
        url = urlparse(src)
        canon_url = normalizeUrl(url, src)
        print("Canon SRC image:", canon_url)
    return canon_url


def getNonImageLinks(current_page_url, link, value, disallowed_rules, db_connection):
    link_value = link.get(value)
    if link_value is not None and len(link_value) != 0:
        # apply disallowed rules
        for rule in disallowed_rules:
            if rule in link_value:
                return None

        url = urlparse(link_value)
        stripped_netloc = eliminateFromURL(url.netloc, EXTRAS)

        # CURRENT_PAGE_URL LINKS WITHOUT BASE IN URL
        if not url.netloc:
            if current_page_url not in link_value:
                link = urljoin("http://" + current_page_url, link_value)
                normalized_url = normalizeUrl(url, link)
            else:
                normalized_url = normalizeUrl(url, link_value)

        # LINKS FROM OTHER SEED SITE
        elif url.netloc and stripped_netloc not in current_page_url:
            for seed in IGNORE_SEED_URLS:
                if seed in url.netloc:
                    return None
            if url.netloc.startswith(IGNORE_DOMAIN_VARIATIONS):
                return None

            # links from the other site from gov domain
            if DOMAIN in url.netloc:
                normalized_url = handleNewDomain(
                    url, link_value, db_connection)
            else:
                return None

        # CURRENT_PAGE_URL LINKS WITH BASE IN URL
        else:
            normalized_url = normalizeUrl(url, link_value)

        if normalized_url is not None:
            # check for images passed as href
            isImage = checkForImage(normalized_url)
            if isImage is not None:
                print("Canon image:", normalized_url)
                return ["IMAGE", normalized_url]
            else:
                print("Canon non image:", normalized_url)
                return ["HTML", normalized_url]

    return None


def normalizeUrl(url, link_value):
    for exc in PATH_EXCLUSIONS:
        if exc in url.path:
            return None

    if url.query or url.fragment or url.scheme == "mailto" or url.scheme == "tel" or url.scheme == "data" or url.scheme == "javascript":
        return None
    '''
    if not url.query and not url.fragment and not url.netloc and not url.path and not url.params:
        return None

    if not url.query and not url.fragment and not url.netloc and url.path == '/' and not url.params:
        return None
    '''
    link_value = eliminateFromURL(link_value, EXTRAS)

    parsed_url = urlcanon.parse_url(link_value)
    urlcanon.whatwg(parsed_url)
    parsed_url_str = str(parsed_url)
    parsed_url_str = parsed_url_str.replace('//', '/')
    if parsed_url_str[0] == '.':
        parsed_url_str = parsed_url_str[1:]
    if parsed_url_str[-1] == '/':
        parsed_url_str = parsed_url_str[:-1]
    return parsed_url_str


def eliminateFromURL(url, array):
    for e in array:
        if e in url:
            url = url.replace(e, "")
    return url


def checkForImage(url):
    for img in IMAGE_CONTENT:
        length = len(img)
        if url[-length:] == img:
            return [url]
    return None


def isPageBinary(url):
    for binary in BINARY_CONTENT:
        length = len(binary)
        if url[-length:] == binary:
            return binary
    return ".html"


def insertImageData(image_url, current_page, db_connection):
    if image_url is not None:
        content_type = image_url.rsplit('.', 1)[1].upper()
        filename = image_url.rsplit('/', 1)[1]
        insertImageDataToDB(current_page, filename,
                            content_type, db_connection)


def handleNonImageSite(href_url, current_page, db_connection):
    page_type = isPageBinary(href_url)
    if page_type == '.html':
        # add to frontier
        duplicate = checkForDuplicateFRONTIER(href_url, db_connection)
        if not duplicate:
            insertPageToDB(href_url, current_page[1], db_connection)
    else:
        insertPageDataToDB(current_page, page_type, db_connection)


def handleNewDomain(url, link_value, db_connection):
    normalized_url = normalizeUrl(
        url, link_value)
    normalized_netloc = normalizeUrl(url, url.netloc)
    if normalized_url is not None:
        duplicate = checkForDuplicateSEED(
            normalized_netloc, db_connection)
        if not duplicate:
            time.sleep(5)
            print("Sleeping for 5s!", normalized_netloc)
            response_robots, sitemap, delay = getResponseRobots(
                normalized_netloc)
            if response_robots != "NOT ALLOWED":
                insertSiteToDB(normalized_netloc, response_robots,
                               sitemap, delay, db_connection)
    return normalized_url
