from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.error
import urllib.robotparser
from socket import timeout
import time
from crawler.consts import *


def getResponseRobots(seed):
    robots_url = 'http://' + seed + '/robots.txt'
    sitemap = None
    response_robots = None
    delay = None

    try:
        time.sleep(5)
        uClient = urlopen(robots_url, timeout=5)
        robots_page = uClient.read()
        uClient.close()
        soup = BeautifulSoup(robots_page, "html.parser")
        response_robots = str(soup)
    except Exception as e:
        print('Fetching robots.txt led to', e)

    if response_robots is not None:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        time.sleep(5)
        rp.read()

        # check if robots are allowed
        url = "http://" + seed
        if not rp.can_fetch(USER_AGENT, url):
            print("Robots are not allowed!")
            return "NOT ALLOWED", 0, 0
        delay = rp.crawl_delay(USER_AGENT)
        sitemap = rp.site_maps()

        # handle redirect
        if '<html>' in response_robots or '<!DOCTYPE html>' in response_robots:
            response_robots = None
    return response_robots, sitemap, delay


def getDisallowedFromRobotsFile(robots_file):
    disallowed = []
    robots_file = robots_file.split("\n")
    for line in robots_file:
        if "Disallow:" in line:
            disallowed.append(line.split(" ")[1])
    return disallowed
