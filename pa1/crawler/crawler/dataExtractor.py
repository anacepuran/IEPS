from db.db import *
import time
import urlcanon
from urllib.parse import urljoin
from crawler.duplicateDetector import *
from urllib.parse import urlparse
from crawler.robots import *
from crawler.consts import *


def fetchData(html_content, current_page, db_connection):
    link_a = None
    images = binary = urls = disallowed_rules = []
    all_new_pages = []
    current_page_ID = current_page[0]
    current_page_seed = current_page[1]
    current_page_url = current_page[3]
    seed_site_data = getSeedSiteFromDB(current_page_seed, db_connection)

    # RESPECT THE CRAWL DELAY
    if seed_site_data is not None:
        crawl_delay = seed_site_data[4]
        if crawl_delay is not None:
            time.sleep(int(crawl_delay))
        # GET DISALLOWED RULES
        robots_file = seed_site_data[2]
        if robots_file is not None:
            disallowed_rules = getDisallowedFromRobotsFile(robots_file)
            allowed_rules = getAllowedFromRobotsFile(robots_file)

    # GET IMG LINKS
    for link in html_content.find_all("img"):
        image_url = getImageLinks(disallowed_rules, link, current_page_url)
        if image_url is not None:
            insertImageData(image_url, current_page_ID, db_connection)

    # GET HREF LINKS
    link_a = html_content.find_all("a")
    if link_a is not None:
        for link in link_a:
            if link.has_attr('href'):
                href_url = getNonImageLinks(
                    link, "href", disallowed_rules, current_page, all_new_pages, db_connection)
                if href_url is not None:
                    handleNonImageSite(
                        href_url, current_page_ID, current_page_seed, all_new_pages, db_connection)

    # GET ONCLICK LINKS
    for link in html_content.find_all(onclick=True):
        onclick_url = getNonImageLinks(
            link, "onclick", disallowed_rules, current_page, all_new_pages, db_connection)
        if onclick_url is not None:
            handleNonImageSite(
                onclick_url, current_page_ID, current_page_seed, all_new_pages, db_connection)

    # BREADTH-FIRST TECHNIQUE IMPLEMENTED --> WAITING FOR THE SITE WITH ID = ID-1 TO PUSH IT'S PAGES TO FRONTIER FIRST
    finnished = None
    while finnished is None or finnished is False:
        finnished = getStatusFromPreviousPage(current_page_ID, db_connection)

    for el in all_new_pages:
        duplicate = checkForDuplicateFRONTIER(el[0], db_connection)
        if not duplicate:
            page_id = insertPageToDB(el[0], el[1], db_connection)
            insertLinkToDB(el[2], page_id, db_connection)
    print("Successfully put all pages into frontier: ", current_page_url)


def getImageLinks(disallowed_rules, link, current_page_url):
    normalized_url = None
    if link.has_attr('src'):
        src = link['src']
        if src is not None and len(src) != 0:
            # apply disallowed rules
            for rule in disallowed_rules:
                if rule in src:
                    return None

            url = urlparse(src)
            normalized_url = normalizeUrl(url, src)
        return normalized_url
    return None


def insertImageData(image_url, site_id, db_connection):
    content_type = filename = None
    if image_url is not None:
        if '.' in image_url:
            content_type = image_url.rsplit('.', 1)[1].upper()
        if '/' in image_url:
            filename = image_url.rsplit('/', 1)[1]
        else:
            filename = image_url
        if content_type is not None and len(content_type) < 5:
            insertImageDataToDB(site_id, filename,
                                content_type, db_connection)
### END IMAGES SECTION ###


### NON-IMAGE SECTION ###
def getNonImageLinks(link, value, disallowed_rules, current_page, all_new_pages, db_connection):
    normalized_url = None
    current_page_url = current_page[3]
    link_value = link.get(value)

    if link_value is not None and len(link_value) != 0:
        # apply disallowed rules
        for rule in disallowed_rules:
            if rule in link_value:
                return None

        url = urlparse(link_value)

        # eliminate images passed as href
        if checkForImage(url.path) is not None:
            return None

        # normalize the netloc extracted from url
        normalized_netloc = eliminateFromURL(url.netloc, EXTRAS)

        # CURRENT_PAGE_URL LINKS WITHOUT BASE IN URLq
        if not url.netloc and current_page_url not in link_value:
            link = urljoin("http://" + current_page_url, link_value)
            normalized_url = normalizeUrl(url, link)

        # LINKS FROM OTHER SITE
        elif url.netloc and normalized_netloc not in current_page_url:
            if normalized_netloc[0] == '.':
                normalized_netloc = normalized_netloc[1:]
            # links from the other site from gov domain
            if DOMAIN in url.netloc:
                handleOtherDomainPage(
                    url, current_page[0], link_value, all_new_pages, db_connection)
                return None

        # CURRENT_PAGE_URL LINKS WITH BASE IN URL
        else:
            normalized_url = normalizeUrl(url, link_value)

    return normalized_url


def handleNonImageSite(url, site_id, seed_site_id, all_new_pages, db_connection):
    page_type = isPageBinary(url)
    if page_type == '.html':
        all_new_pages.append([url, seed_site_id, site_id])
    else:
        insertPageDataToDB(site_id, page_type, db_connection)
### END NON-IMAGE SECTION ###


### OTHER DOMAIN PAGE ###
def handleOtherDomainPage(url, current_page_id, link_value, all_new_pages, db_connection):
    normalized_url = normalizeUrl(
        url, link_value)
    normalized_netloc = normalizeUrl(url, url.netloc)

    if normalized_url is not None:
        duplicate_seed = checkForDuplicateSEED(
            normalized_netloc, db_connection)
        duplicate_page = checkForDuplicateFRONTIER(
            normalized_url, db_connection)

        # FIRST TIME HANDLING THIS DOMAIN --> ADD TO SITE TABLE
        if not duplicate_seed:
            print("New page from other domain: ",
                  normalized_netloc, normalized_url)
            response_robots, sitemap, delay = getResponseRobots(
                normalized_netloc, db_connection)
            if response_robots != "NOT ALLOWED":
                seed_site_id = insertSiteToDB(normalized_netloc, response_robots,
                                              sitemap, delay, db_connection)
                handleNonImageSite(normalized_url, current_page_id,
                                   seed_site_id, all_new_pages, db_connection)

        # DOMAIN ALREADY IN SITE TABLE --> ADD NEW PAGE FROM THIS DOMAIN
        if duplicate_seed and not duplicate_page:
            duplicate_seed_id = duplicate_seed[0]
            handleNonImageSite(
                normalized_url, current_page_id, duplicate_seed_id, all_new_pages, db_connection)
### END OTHER DOMAIN PAGE ###


### AUX FUNCTIONS ###
def normalizeUrl(url, link_value):
    for exc in PATH_EXCLUSIONS:
        if exc in url.path:
            return None

    if url.query or url.fragment or url.scheme == "mailto" or url.scheme == "tel" or url.scheme == "data" or url.scheme == "javascript":
        return None

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
### END AUX FUNCTIONS ###
