# extract the data - images, hyperlinks
from db.db import *
import time

'''
When your crawler fetches and renders a web page, do some simple parsing to detect images and next links.
When parsing links, include links from href attributes and onclick Javascript events (e.g. location.href or document.location). 
Be careful to correctly extend the relative URLs before adding them to the frontier.
Detect images on a web page only based on img tag, where the src attribute points to an image URL.
Donwload HTML content only. List all other content (.pdf, .doc, .docx, .ppt and .pptx) in the page_data table - there is no need to populate 
data field (i.e. binary content). In case you put a link into a frontier and identify content as a binary source, 
you can just set its page_type to BINARY. The same holds for the image data.
'''


def fetchData(current_page, db_connection):
    # AT THIS POINT PAGE COULD ONLY BE UNDUPLICATED HTML
    robots_file = getRobotsFileContent(current_page, db_connection)

    # respect the crawl_delay
    crawl_delay = getCrawlDelayContent(current_page, db_connection)
    if crawl_delay is not None:
        time.sleep(crawl_delay)

    # TO DO: APPLY ROBOTS.TXT - DISALLOWED RULES
    # TO DO: EXTRACT IMAGES ADD THEM TO THE IMAGE_DATA --> DON'T FORGET TO EXTEND URLS WITH THE BASE URL
    # TO DO: EXTRACT PAGES AND ADD TO FRONTIER --> DON'T ADD THEM DO PAGES_DATA
    # TO DO: EXTRACT URLS, CANONICALIZE THEM AND ADD THEM TO THE FRONTIER

    return 0
