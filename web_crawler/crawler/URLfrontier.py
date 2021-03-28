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
import sys

sys.setrecursionlimit(1500)


def processSeedPages(seed_urls, db_connection):
    for seed in seed_urls:
        if checkForDuplicateSEED(seed, db_connection) or checkForDuplicateFRONTIER(seed, db_connection):
            continue

        response_robots, sitemap, delay = getResponseRobots(
            seed, db_connection)
        if response_robots != "NOT ALLOWED":
            site_id = insertSiteToDB(
                seed, response_robots, sitemap, delay, db_connection)
            page_id = insertPageToDB(seed, site_id, db_connection)


def processCurrentPage(current_page, db_connection):
    html_content = status_code = content_type = None
    url = "http://" + current_page[3]

    html_content, status_code, content_type = getContent(url)
    if content_type is not None and "html" in content_type:
        if html_content is not None and status_code is not None:
            pretty_content = html_content.prettify()
            hashed_content = hashlib.md5(
                pretty_content.encode()).hexdigest()

            duplicate = checkForDuplicateHTML(
                current_page[0], hashed_content, db_connection)

            if status_code >= 400:
                updatePageAsInaccessible(
                    current_page[0], status_code, db_connection)
                print("Inaccessible: ", status_code, url)
            else:
                if not duplicate:
                    fetchData(html_content, current_page, db_connection)
                    updatePageAsHTML(current_page[0], status_code,
                                     pretty_content, hashed_content, db_connection)
                else:
                    print("Duplicate", current_page[3], duplicate[0])
                    updatePageAsDuplicate(current_page[0], status_code,
                                          duplicate, db_connection)
        else:
            updatePageAsInaccessible(
                current_page[0], "INACCESSIBLE", db_connection)
    else:
        updatePageAsInaccessible(
            current_page[0], "INACCESSIBLE", db_connection)


def getContent(url):
    soup = status_code = content_type = None
    try:
        response = requests.get(url, data={'key': 'value'})
        status_code = response.status_code
        content_type = response.headers['Content-Type']
        time.sleep(5)
    except Exception as e:
        print("Getting status code led to", e)
        return soup, status_code, content_type

    soup = None
    options = Options()
    options.headless = True
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--user-agent=fri-wier-norci")
    try:
        time.sleep(5)
        driver = webdriver.Chrome(executable_path=os.path.abspath(
            "./crawler/webdriver/chromedriver.exe"), options=options)
        driver.set_page_load_timeout(6)
        driver.get(url)
        html_content = driver.page_source
        driver.close()
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as error:
        print("Running Selenium led to", error)

    return soup, status_code, content_type
