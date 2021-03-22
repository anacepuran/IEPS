from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from crawler.duplicateDetector import *
from crawler.dataExtractor import *
import hyperlink
from db.db import *
from crawler.robots import *
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import hashlib
import os
import requests
import urllib.error
from socket import timeout

'''
The frontier strategy needs to follow the breadth-first strategy. In the report explain how is your strategy implemented.
Check and respect the robots.txt file for each domain if it exists. 
Correctly respect the commands User-agent, Allow, Disallow, Crawl-delay and Sitemap. 
Make sure to respect robots.txt as sites that define special crawling rules often contain spider traps. 
Also make sure that you follow ethics and do not send request to the same server more often than one request in 5 seconds (not only domain but also IP!).
'''


def processSeedPages(seed_urls, db_connection):
    for seed in seed_urls:
        if checkForDuplicateSEED(seed, db_connection) or checkForDuplicateFRONTIER(seed, db_connection):
            continue

        response_robots, sitemap, delay = getResponseRobots(seed)

        site_id = insertSiteToDB(
            seed, response_robots, sitemap, delay, db_connection)
        page_id = insertPageToDB(seed, site_id, db_connection)


def processCurrentPage(current_page, db_connection):
    url = "http://" + current_page[3]

    html_content, status_code = getContent(url)
    if html_content is not None and status_code is not None:
        pretty_content = html_content.prettify()
        hashed_content = hashlib.md5(pretty_content.encode()).hexdigest()

        duplicate = checkForDuplicateHTML(
            current_page[0], hashed_content, db_connection)

        if status_code >= 400:
            updatePageAsInaccessible(
                current_page, status_code, db_connection)
            print("Inaccessible: ", status_code, url)
        else:
            if not duplicate:
                fetchData(html_content, current_page, db_connection)
                updatePageAsHTML(current_page, status_code,
                                 pretty_content, hashed_content, db_connection)
            else:
                updatePageAsDuplicate(current_page, status_code,
                                      duplicate, db_connection)
    # elif status_code is None: delete url from page and site


def getContent(url):
    soup = status_code = None
    try:
        response = requests.get(url)
        status_code = response.status_code
        time.sleep(5)
    except Exception as e:
        print("Getting status code led to", e)

    options = Options()
    options.headless = True
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--user-agent=fri-wier-norci")

    try:
        driver = webdriver.Chrome(executable_path=os.path.abspath(
            "./crawler/webdriver/chromedriver.exe"), options=options)
        driver.get(url)
        driver.set_page_load_timeout(10)
        driver.implicitly_wait(4)
        html_content = driver.page_source
        driver.close()
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as error:
        print("Running Selenium led to", error)
    except timeout:
        print("Running Selenium led to timeout error", url)

    return soup, status_code
