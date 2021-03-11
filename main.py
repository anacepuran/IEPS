import sys
import threading
from db.db import *
import crawler.dataExtractor
import crawler.duplicateDetector
from crawler.URLfrontier import *
import time

# seed_urls = ['https://www.gov.si/assets/ministrstva/MDDSZ/druzina/Obrazec-S1-1.pdf']
seed_urls = ['gov.si', 'evem.gov.si', 'e-uprava.gov.si', 'e-prostor.gov.si']
domain = '.gov.si'


class current_thread(threading.Thread):
    def __init__(self, threadID, db_connection):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.db_connection = db_connection
        print(f"Web Crawler worker {self.threadID} has Started")

    def run(self):
        current_page = None
        while True:
            current_page = getFirstFromFrontier(self.db_connection)
            if current_page is not None:
                print(self.threadID)
                processCurrentPage(current_page, domain, self.db_connection)
            else:
                break
        print(self.threadID, " finnished!")


def initiateCrawler(number_of_workers):
    current_page, db_connection = initiateConnectionToDatabase(seed_urls)

    if not current_page:
        processSeedPages(seed_urls, db_connection)

    all_threads = []
    for i in range(number_of_workers):
        thread = current_thread(i, db_connection)
        all_threads.append(thread)
        thread.start()
        time.sleep(5)

    # wait for the threads to finish
    for t in all_threads:
        t.join()
    print("All threads have finnished!")
    closeConnectionToDatabase()


if __name__ == '__main__':
    number_of_workers = int(sys.argv[1])

    # run: python main.py <number_of_workers>
    initiateCrawler(number_of_workers)
