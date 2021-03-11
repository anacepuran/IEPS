import hashlib

'''
In a database store canonicalized URLs only!
During crawling you need to detect duplicate web pages. The easiest solution is to check whether a web page with the same 
page content was already parsed (hint: you can extend the database with a hash, otherwise you need compare exact HTML code). 
If your crawler gets a URL from a frontier that has already been parsed, this is not treated as a duplicate. In such cases there 
is no need to re-crawl the page, just add a record into to the table link accordingly.
'''


def checkForDuplicateURL(url, param, db_connection):
    cur = db_connection.cursor()
    try:
        sql_query = "SELECT id FROM crawldb.page WHERE %s=%s"
        cur.execute(sql_query, (param, url,))
        current_site_id = cur.fetchall()
        print("Current site id: ", current_site_id)
    except Exception as error:
        print("Checking for URL duplicates led to", error)
    return current_site_id


# SHOULD html.prettyfy() before calling this function !!!!
# IF duplicate_page_id == None ==> no duplicates
def checkForDuplicateHTML(page_id, hashed_content, db_connection):
    cur = db_connection.cursor()
    try:
        sql_query = "SELECT id FROM crawldb.page WHERE id != %s AND page_hash = %s"
        cur.execute(sql_query, (page_id, hashed_content,))
        duplicate_page = cur.fetchall()
    except Exception as error:
        print("Checking for HTML duplicates led to", error)
    return duplicate_page
