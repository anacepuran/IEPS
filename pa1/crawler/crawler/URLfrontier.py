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
import time

sys.setrecursionlimit(1500)


def processSeedPages(seed_urls, db_connection):
    for seed in seed_urls:
        if checkForDuplicateSEED(seed, db_connection) or checkForDuplicateFRONTIER(seed, db_connection):
            continue

        response_robots, sitemap, delay = getResponseRobots(seed, db_connection)

        site_id = insertSiteToDB(seed, response_robots, sitemap, delay, db_connection)
        page_id = insertPageToDB(seed, site_id, db_connection)


def processCurrentPage(current_page, db_connection, driver):
    html_content = status_code = content_type = None
    url = "http://" + current_page[3]

    html_content, status_code, content_type = getContent(url, driver)

    if html_content is not None and status_code is not None:
        # 1. PAGE TYPE IS HTML
        if content_type is not None and 'html' in content_type:
            # 1.1 hash and search duplicates
            pretty_content = html_content.prettify()
            hashed_content = hashlib.md5(pretty_content.encode()).hexdigest()
            duplicate = checkForDuplicateHTML(current_page[0], hashed_content, db_connection)

            # 1.2 check if page is accessible
            if status_code >= 400:
                updatePageAsInaccessible(current_page[0], status_code, "HTML", db_connection)
                print("Inaccessible: ", status_code, url, current_page[0])
            else:
                # 1.3 if page is not duplicate - crawl it 
                if not duplicate:
                    fetchData(html_content, current_page, db_connection)
                    updatePageAsHTML(current_page[0], status_code,pretty_content, hashed_content, db_connection)
                else:
                    print("Duplicate: ", current_page[3], duplicate[0])
                    updatePageAsDuplicate(current_page[0], status_code,duplicate, db_connection)
        # 2. PAGE TYPE IS NOT HTML
        else:
            updatePageAsNotHTML(current_page[0], status_code, db_connection)
            print("Not HTML: ", current_page[3])
    else:
        updatePageAsInaccessible(current_page[0], status_code, None, db_connection)
        print("Not a page: ", current_page[3], current_page[0])


def getContent(url, driver):
    soup = status_code = content_type = None
    try:
        time.sleep(6)
        response = requests.get(url, data={'key': 'value'})
        status_code = response.status_code
        content_type = response.headers['Content-Type']
    except Exception as e:
        print("Getting status code led to", e)
        return soup, status_code, content_type
    
    now = datetime.now()
    access_time = now.strftime("%Y-%m-%d %H:%M:%S'")
    print("ACCESS 1:", url, access_time)

    try:
        time.sleep(6)
        driver.get(url)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as error:
        print("Fetching page with Selenium led to", error)

    now = datetime.now()
    access_time = now.strftime("%Y-%m-%d %H:%M:%S'")
    print("ACCESS 2:", url, access_time)

    return soup, status_code, content_type
