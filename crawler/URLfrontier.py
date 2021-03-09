from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
from urllib.parse import urljoin, urlparse
import urllib.error
import urllib.robotparser
from crawler.duplicateDetector import checkForDuplicateURL
import hyperlink

'''
The frontier strategy needs to follow the breadth-first strategy. In the report explain how is your strategy implemented.
Check and respect the robots.txt file for each domain if it exists. 
Correctly respect the commands User-agent, Allow, Disallow, Crawl-delay and Sitemap. 
Make sure to respect robots.txt as sites that define special crawling rules often contain spider traps. 
Also make sure that you follow ethics and do not send request to the same server more often than one request in 5 seconds (not only domain but also IP!).
'''
user_agent = "fri-wier-norci"


def processSeedPages(seed_urls, domains, db_connection):
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

        # respect User-Agent
        if rp.can_fetch(user_agent, seed) is False:
            print("Robots not allowed")
            return

        # respect Crawl-delay
        delay = rp.crawl_delay(user_agent)
        if delay is not None:
            time.sleep(delay)

    return 0


def getResponseRobots(url):
    soup_string = None

    try:
        uClient = uReq(url)
        robots_page = uClient.read()
        uClient.close()
        soup = BeautifulSoup(robots_page, "html.parser")
        soup_string = str(soup)
    except urllib.error.HTTPError as e:
        print('HTTPError: {}'.format(e.code))

    return soup_string


def getSitemap(robots):
    smap = []
    for line in robots.splitlines():
        if "Sitemap" in line:
            if line.startswith("Sitemap"):
                smap.append(line.split(' ')[1])
            else:
                smap.append(line.split('Sitemap: ')[1])
    return smap


def insertSiteToDB(url, response_robots, sitemap, db_connection):
    site_id = None
    cur = db_connection.cursor()

    try:
        sql_query = """INSERT into crawldb.site (domain, robots_content, sitemap_content) 
                        VALUES (%s, %s, %s) 
                        RETURNING id """
        cur.execute(sql_query, (url, response_robots, sitemap))
        site_id = cur.fetchone()[0]
        db_connection.commit()
    except Exception as error:
        print(error)
    return site_id
