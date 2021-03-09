import sys
import threading
from db.db import initiateConnectionToDatabase
import crawler.dataExtractor
import crawler.duplicateDetector

#seed_urls = ['e-uprava.gov.si']
seed_urls = ['e-uprava.gov.si', 'gov.si', 'evem.gov.si', 'e-prostor.gov.si']
domains = '.gov.si'
all_threads = []


class multiple_threads(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        print(f"Web Crawler worker {threading.current_thread()} has Started")

    def run(self):
        return 0


def initiate_crawler(number_of_workers):
    initiateConnectionToDatabase(seed_urls, domains)

    for i in range(number_of_workers):
        thread = multiple_threads(i)
        thread.start()
        all_threads.append(thread)

    # wait for the threads to finish
    for t in all_threads:
        t.join()
    print("All threads have finnished!")


if __name__ == '__main__':
    number_of_workers = int(sys.argv[1])

    # run: python main.py <number_of_workers>
    initiate_crawler(number_of_workers)
