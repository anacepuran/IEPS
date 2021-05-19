from db.db import *
import time
import re
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
        # GET ALLOWED & DISALLOWED RULES
        robots_file = seed_site_data[2]
        if robots_file is not None:
            disallowed_rules = getDisallowedFromRobotsFile(robots_file)
            allowed_rules = getAllowedFromRobotsFile(robots_file)

    # 1. GET IMG LINKS
    for link in html_content.find_all("img"):
        image_url = getImageLinks(disallowed_rules, link, current_page_url)
        if image_url is not None:
            insertImageData(image_url, current_page_ID, db_connection)

    # 2. GET HREF LINKS
    link_a = html_content.find_all("a")
    if link_a is not None:
        for link in link_a:
            if link.has_attr('href'):
                href_url = getNonImageLinks(link, html_content, "href", disallowed_rules, current_page, all_new_pages, db_connection)
                if href_url is not None and DOMAIN in href_url:
                    handleNonImageSite(href_url, current_page_ID, current_page_seed, all_new_pages, db_connection)

    # 3. GET ONCLICK LINKS
    for link in html_content.find_all(onclick=True):
        onclick_url = getNonImageLinks(link, html_content, "onclick", disallowed_rules, current_page, all_new_pages, db_connection)
        if onclick_url is not None and DOMAIN in href_url:
            handleNonImageSite(onclick_url, current_page_ID, current_page_seed, all_new_pages, db_connection)


    """ BREADTH-FIRST TECHNIQUE IMPLEMENTED --> WAITING FOR THE SITE WITH ID = ID-1 TO PUSH IT'S PAGES TO FRONTIER FIRST """
    finnished = False
    while finnished is False:
        finnished = getStatusFromPreviousPage(current_page_ID, db_connection)

    for el in all_new_pages:
        duplicate = checkForDuplicateFRONTIER(el[0], db_connection)
        if not duplicate:
            page_id = insertPageToDB(el[0], el[1], db_connection)
            insertLinkToDB(el[2], page_id, db_connection)
    print("Successfully put all pages into frontier: ", current_page_url, current_page[0])


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
            insertImageDataToDB(site_id, filename, content_type, db_connection)
### END IMAGES SECTION ###


### NON-IMAGE SECTION ###
def getNonImageLinks(link, html_content, value, disallowed_rules, current_page, all_new_pages, db_connection):
    normalized_url = None
    current_page_url = current_page[3]
    link_value = link.get(value)
    base_line = None

    # HANDLE "ONCLICK" LINKS --> GET URL
    if value == 'onclick':
        temp_link_value = extractOnClick(link_value)
        link_value = temp_link_value

    if link_value is not None and len(link_value) != 0:
        # apply disallowed rules
        for rule in disallowed_rules:
            if rule in link_value:
                return None

        url = urlparse(link_value)
        base_line = html_content.find("base")

        # eliminate images passed as href
        if checkForImage(url.path) is not None:
            return None

        # normalize the netloc extracted from link
        normalized_netloc = eliminateFromURL(url.netloc, EXTRAS)
        if normalized_netloc and normalized_netloc[0] == '.':
            normalized_netloc = normalized_netloc[1:]

        # 1. RELATIVE LINK WITHOUT BASE - EXTEND WITH BASE
        if not url.netloc and current_page_url not in link_value:
            # 1.1 extract with base_url
            if base_line != None and base_line.has_attr('href') and value == "href":
                base_url = base_line.get(value)
                if base_url != '/':
                    # //www.stopbirokraciji.com 
                    if base_url[0] == '/':
                        base_url = base_url[1:]
                    if base_url[0] == '/':
                        base_url = base_url[1:]
                    normalized_base = eliminateFromURL(base_url, EXTRAS)
                    link = urljoin("http://" + normalized_base, link_value)
                else:
                    link = urljoin("http://" + current_page_url, link_value)
                    print(link)
            # 1.2 extract with current_page_url
            else:
                link = urljoin("http://" + current_page_url, link_value)
            normalized_url = normalizeUrl(url, link)

        # 2. LINKS FROM OTHER SITE/DOMAIN - INSER INTO SITE IF IT'S SLO GOV DOMAIN
        elif url.netloc and normalized_netloc not in current_page_url:
            if DOMAIN in url.netloc:
                handleOtherDomainPage(url, current_page[0], link_value, all_new_pages, db_connection)
                return None

        # 3. CURRENT_PAGE_URL LINKS WITH BASE - ALREADY EXTENDED
        else:
            normalized_url = normalizeUrl(url, link_value)

    return normalized_url


def handleNonImageSite(url, site_id, seed_site_id, all_new_pages, db_connection):
    page_type = pageType(url)
    if page_type == '.html':
        all_new_pages.append([url, seed_site_id, site_id])
    else:
        insertPageDataToDB(site_id, page_type, db_connection)
### END NON-IMAGE SECTION ###


### OTHER DOMAIN PAGE ###
def handleOtherDomainPage(url, current_page_id, link_value, all_new_pages, db_connection):
    normalized_url = normalizeUrl(url, link_value)
    normalized_netloc = normalizeUrl(url, url.netloc)

    if normalized_url is not None:
        duplicate_seed = checkForDuplicateSEED(normalized_netloc, db_connection)
        duplicate_page = checkForDuplicateFRONTIER(normalized_url, db_connection)

        # FIRST TIME HANDLING THIS DOMAIN --> ADD TO SITE TABLE
        if not duplicate_seed:
            print("New page from other .gov.si domain: ", normalized_netloc, normalized_url)
            response_robots, sitemap, delay = getResponseRobots(normalized_netloc, db_connection)
            if response_robots != "NOT ALLOWED":
                seed_site_id = insertSiteToDB(normalized_netloc, response_robots, sitemap, delay, db_connection)
                handleNonImageSite(normalized_url, current_page_id, seed_site_id, all_new_pages, db_connection)

        # DOMAIN ALREADY IN SITE TABLE --> JUST ADD NEW PAGE FROM THIS DOMAIN
        if duplicate_seed and not duplicate_page:
            duplicate_seed_id = duplicate_seed[0]
            handleNonImageSite(normalized_url, current_page_id, duplicate_seed_id, all_new_pages, db_connection)
### END OTHER DOMAIN PAGE ###


### AUX FUNCTIONS ###
def normalizeUrl(url, link_value):
    parsed_url_str = None
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
    if parsed_url_str: 
        if parsed_url_str[0] == '.':
            parsed_url_str = parsed_url_str[1:]
        if parsed_url_str[-1] == '/':
            parsed_url_str = parsed_url_str[:-1]
    return parsed_url_str


def extractOnClick(link_value):
    onclick_link = None
    link_before = re.search(
        "((document|window|parent).)?location(.href)?=", link_value)
    if link_before:
        link_before = link_before.group(0)
        onclick_link = link_value.replace(link_before, "").replace("'", "")
    return onclick_link


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


def pageType(url):
    for binary in BINARY_CONTENT:
        length = len(binary)
        if url[-length:] == binary:
            return binary
    return ".html"
### END AUX FUNCTIONS ###
