# extract the data - images, hyperlinks

'''
When your crawler fetches and renders a web page, do some simple parsing to detect images and next links.
When parsing links, include links from href attributes and onclick Javascript events (e.g. location.href or document.location). 
Be careful to correctly extend the relative URLs before adding them to the frontier.
Detect images on a web page only based on img tag, where the src attribute points to an image URL.
Donwload HTML content only. List all other content (.pdf, .doc, .docx, .ppt and .pptx) in the page_data table - there is no need to populate 
data field (i.e. binary content). In case you put a link into a frontier and identify content as a binary source, 
you can just set its page_type to BINARY. The same holds for the image data.
'''


def extractData():
    return 0
