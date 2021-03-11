from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
import urllib.error
import urllib.robotparser
from crawler.duplicateDetector import *
import hyperlink
from db.db import *
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import hashlib
import os
import requests

'''
The frontier strategy needs to follow the breadth-first strategy. In the report explain how is your strategy implemented.
Check and respect the robots.txt file for each domain if it exists. 
Correctly respect the commands User-agent, Allow, Disallow, Crawl-delay and Sitemap. 
Make sure to respect robots.txt as sites that define special crawling rules often contain spider traps. 
Also make sure that you follow ethics and do not send request to the same server more often than one request in 5 seconds (not only domain but also IP!).
'''
USER_AGENT = "fri-wier-norci"


def processSeedPages(seed_urls, db_connection):
    for seed in seed_urls:
        if checkForDuplicateURL(seed, "domain", db_connection):
            continue

        robots_url = 'http://' + seed + '/robots.txt'
        response_robots = getResponseRobots(robots_url)
        sitemap = None
        if response_robots is not None:
            # get sitemaps
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            sitemap = rp.site_maps()

        site_id = insertSiteToDB(seed, response_robots, sitemap, db_connection)
        page_id = insertPageToDB(seed, site_id, db_connection)
    return "Done!"


def getResponseRobots(url):
    soup_string = None

    try:
        uClient = urlopen(url)
        robots_page = uClient.read()
        uClient.close()
        soup = BeautifulSoup(robots_page, "html.parser")
        soup_string = str(soup)
    except urllib.error.HTTPError as e:
        print('HTTPError: {}'.format(e.code))

    return soup_string


def processCurrentPage(current_page, domain, db_connection):
    url = "http://" + current_page[3]
    print("Current page URL: ", url)

    http_status_code = getStatusCode(url)

    if http_status_code >= 400:
        updatePageAsInaccessible(current_page, http_status_code, db_connection)
        return "INACCESSIBLE"

    # TO DO: APPLY ROBOTS.TXT: USER_AGENT RULER AND SITEMAPS HERE
    # IMPORTANT: PROŠNJE LAHKO POIŠLJAŠ NA ISTI STREŽNIK Z RAZMAKOM 5s

    # TO DO: CHECK THE TYPE OF THE DATA ON THE PAGE
    binary = False

    if not binary:
        html_content = getContent(url)
        hashed_content = hashlib.md5(html_content.encode()).hexdigest()
        duplicate = checkForDuplicateHTML(
            current_page[0], hashed_content, db_connection)

        if not duplicate:
            # AT THIS POINT PAGE COULD ONLY BE UNDUPLICATED HTML
            # TO DO: APPLY ROBOTS.TXT - DISALLOWED RULES
            # TO DO: EXTRACT IMAGES AND DATA AND ADD THEM TO THE PAGE_DATA AND IMAGE_DATA (PDF, DOC, ...) --> DON'T FORGET TO EXTEND URLS WITH THE BASE URL
            # TO DO: EXTRACT URLS, CANONICALIZE THEM AND ADD THEM TO THE FRONTIER AND PAGE_DATA (HMTL)
            fetchData(current_page, db_connection)
        else:
            updatePageAsDuplicate(current_page, duplicate, db_connection)
    else:
        # TO DO: POST DATA TO PAGE_DATA TABLE
        insertPageDataToDB()
        updatePageAsBinary()

    return 0


def getStatusCode(url):
    response = requests.get(url)
    return response.status_code


def getContent(url):
    options = Options()
    options.headless = True
    options.add_argument('--ignore-certificate-errors')
    try:
        driver = webdriver.Chrome(executable_path=os.path.abspath(
            "./crawler/webdriver/chromedriver.exe"), options=options)
        driver.get(url)
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(4)
    except Exception as error:
        print("Running Selenium led to", error)

    html_content = driver.page_source
    driver.close()
    soup = BeautifulSoup(html_content, "html.parser")
    pretty_content = soup.prettify()
    return pretty_content


def fetchData(current_page, db_connection):
    return 0
