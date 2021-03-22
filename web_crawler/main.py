import sys
import threading
from db.db import *
import crawler.dataExtractor
import crawler.duplicateDetector
from crawler.URLfrontier import *
import time

#SEED_URLS = ['gov.si', 'evem.gov.si', 'e-uprava.gov.si', 'e-prostor.gov.si']
SEED_URLS = ['e-prostor.gov.si']


class current_thread(threading.Thread):
    def __init__(self, threadID, db_connection):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.db_connection = db_connection
        print(f"Web Crawler worker {self.threadID} has Started")

    def run(self):
        current_page = None
        while True:
            time.sleep(5)
            print("Sleeping for 5s!")
            current_page = getFirstFromFrontier(self.db_connection)
            if current_page is not None:
                # edit multithreading to go breath first !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print("Current page in FRONTIER: ", current_page[3])
                processCurrentPage(current_page, self.db_connection)
            else:
                break
        print(self.threadID, " finnished!")


def initiateCrawler(number_of_workers):
    current_page, db_connection = initiateConnectionToDatabase(SEED_URLS)

    if not current_page:
        processSeedPages(SEED_URLS, db_connection)

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

    initiateCrawler(number_of_workers)
