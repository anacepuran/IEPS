import sys
import threading
from db.db import *
import crawler.dataExtractor
import crawler.duplicateDetector
from crawler.URLfrontier import *
import time
from crawler.consts import *
from selenium.webdriver.firefox.options import Options


lock = threading.Lock()


class current_thread(threading.Thread):
    def __init__(self, threadID, db_connection):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.db_connection = db_connection
        print(f"Web Crawler worker {self.threadID} has Started")

    def run(self):
        try:
            options = Options()
            options.headless = True
            options.add_argument("--user-agent=fri-wier-norci")
            driver = webdriver.Firefox(executable_path=os.path.abspath(
                "./crawler/webdriver/geckodriver.exe"), options=options)
            driver.set_page_load_timeout(12)
        except Exception as error:
            print("Running Selenium led to", error)

        current_page = None
        while True:
            with lock:
                current_page = getFirstFromFrontier(self.db_connection)
                print("Current page in FRONTIER: ", current_page[3], current_page[0], self.threadID)

            if current_page is not None:
                processCurrentPage(current_page, self.db_connection, driver)
            else:
                driver.close()
                break
        print(self.threadID, " worker finnished!")


def initiateCrawler(number_of_workers):
    current_page, db_connection = initiateConnectionToDatabase(SEED_URLS)

    if not current_page:
        processSeedPages(SEED_URLS, db_connection)

    # CHANGE ACCESSED_TIME TO NULL IF FINNISHED = FALSE --> RESET FRONTIER AFTER STOPPING THE CRAWLER
    reset = True
    while reset == True:
        reset = resetFrontier(db_connection)
    
    all_threads = []
    for i in range(number_of_workers):
        thread = current_thread(i, db_connection)
        all_threads.append(thread)
        thread.start()

    for t in all_threads:
        t.join()
    print("All threads have finnished!")
    closeConnectionToDatabase()


if __name__ == '__main__':
    number_of_workers = int(sys.argv[1])

    initiateCrawler(number_of_workers)
