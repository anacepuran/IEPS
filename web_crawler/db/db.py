import psycopg2
from psycopg2 import pool
from datetime import datetime
import threading
from crawler.consts import *

lock = threading.Lock()
db_pool = None


def initiateConnectionToDatabase(seed_urls):
    # initiate connection
    try:
        db_pool = pool.ThreadedConnectionPool(3, 10, user=DB_['username'], password=DB_['password'],
                                              host=DB_['host'], port=DB_['port'], database=DB_['db_name'])
        if db_pool:
            print('PostgreSQL connection pool is succesfully created!')
        else:
            print('PostgreSQL connection pool couldn\'t be established!')
    except Exception as error:
        print(error)

    db_connection = db_pool.getconn()
    cur = db_connection.cursor()

    # check whether frontier is empty
    sql_query = "SELECT * FROM crawldb.page LIMIT 1"
    cur.execute(sql_query)
    current_page = cur.fetchone()
    return [current_page, db_connection]


def closeConnectionToDatabase():
    try:
        if db_pool:
            db_pool.closeall()
            print('PostgreSQL connection pool is closed!')
    except Exception as error:
        print("Closing the database connection led to", error)


# POST SITE
def insertSiteToDB(url, response_robots, sitemap, delay, db_connection):
    site_id = None

    cur = db_connection.cursor()
    with lock:
        try:
            sql_query = """ INSERT into crawldb.site (domain, robots_content, sitemap_content, crawldelay_content)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id """
            cur.execute(sql_query, (url, response_robots, sitemap, delay))
            site_id = cur.fetchone()[0]
            db_connection.commit()
        except Exception as error:
            print("Inserting the site to the database led to", error)
    return site_id


# GET SITE
def getSeedSiteFromDB(seed_site_id, db_connection):
    robots_site = None

    cur = db_connection.cursor()
    try:
        sql_query = """ SELECT * FROM crawldb.site
                        WHERE id = %s """
        cur.execute(sql_query, (seed_site_id, ))
        robots_site = cur.fetchone()
    except Exception as error:
        print("Fetching robots file led to", error)
    return robots_site


# GET FIRST UNPROCESSED PAGE
def getFirstFromFrontier(db_connection):
    accessed_current_page = None

    cur = db_connection.cursor()
    with lock:
        try:
            sql_query = """ SELECT * FROM crawldb.page
                            WHERE finnished IS %s
                            ORDER BY id asc
                            LIMIT 1 """
            cur.execute(sql_query, (False, ))
            current_page = cur.fetchone()
            if current_page is not None:
                now = datetime.now()
                access_time = now.strftime("%Y-%m-%d %H:%M:%S'")

                sql_query = """ UPDATE crawldb.page
                                SET accessed_time = %s
                                WHERE id = %s
                                RETURNING * """
                cur.execute(sql_query, (access_time, current_page[0]))
                accessed_current_page = cur.fetchone()
                db_connection.commit()
        except Exception as error:
            print("Getting the first site from the frontier led to", error)
    return accessed_current_page


# POST PAGE
def insertPageToDB(url, site_id, db_connection):
    page_id = None
    page_type_code = "HTML"
    finnished = False

    cur = db_connection.cursor()
    with lock:
        try:
            sql_query = """ INSERT into crawldb.page (site_id, url, page_type_code, finnished)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id """
            cur.execute(sql_query, (site_id, url, page_type_code, finnished))
            page_id = cur.fetchone()[0]
            db_connection.commit()
        except Exception as error:
            print("Inserting the page to the frontier led to", error)
    return page_id


# PUT PAGE - DUPLICATE
def updatePageAsDuplicate(site_id, status_code, duplicate, db_connection):
    duplicate_page = None
    page_type_code = "DUPLICATE"
    first = duplicate[0]
    html_content = "NULL"
    finnished = True

    cur = db_connection.cursor()
    try:
        sql_query = """ UPDATE crawldb.page
                        SET http_status_code = %s, page_type_code = %s, html_content = %s, finnished = %s
                        WHERE id = %s
                        RETURNING * """
        cur.execute(sql_query, (status_code, page_type_code,
                                html_content, finnished, site_id))
        duplicate_page = cur.fetchone()
        sql_query = """ INSERT INTO crawldb.link
                        (from_page, to_page) VALUES (%s, %s)
                        RETURNING * """
        cur.execute(sql_query, (first, site_id))
        duplicate_link = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Updating page as duplicate in frontier led to", error)
    return duplicate_page


# PUT PAGE - INACCESSIBLE
def updatePageAsInaccessible(site_id, http_status_code, db_connection):
    html_content = "NULL"
    finnished = True

    cur = db_connection.cursor()
    try:
        sql_query = """ UPDATE crawldb.page
                        SET html_content = %s, http_status_code = %s, finnished = %s
                        WHERE id = %s
                        RETURNING * """
        cur.execute(sql_query, (html_content,
                                http_status_code, finnished, site_id))
        inaccessible_page = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Updating page as inaccessible in frontier led to", error)
    return inaccessible_page


# PUT PAGE - HTML
def updatePageAsHTML(current_page_id, http_status_code, html_content, hashed_content, db_connection):
    html_page = None
    finnished = True
    # UPDATE TO ADD HTML !!!!!!!!!!!!!!!!!!!!!

    cur = db_connection.cursor()
    try:
        sql_query = """ UPDATE crawldb.page
                        SET http_status_code = %s, page_hash=%s, finnished=%s
                        WHERE id = %s
                        RETURNING * """
        cur.execute(sql_query, (
            http_status_code, hashed_content, finnished, current_page_id))
        html_page = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Updating page as HTML in frontier led to", error)
    return html_page


# GET PAGE STATUS - FINNISHED/NOT
def getStatusFromPreviousPage(current_page_ID, db_connection):
    page_status = None
    cur = db_connection.cursor()
    try:
        sql_query = """ SELECT * FROM crawldb.page
                        WHERE id = %s"""
        cur.execute(sql_query, (current_page_ID, ))
        page_status = cur.fetchone()[8]
        db_connection.commit()
    except Exception as error:
        print("Getting status led to: ", error)
    return page_status


# POST LINK
def insertLinkToDB(site_id, page_id, db_connection):
    link = None

    cur = db_connection.cursor()
    try:
        sql_query = """ INSERT INTO crawldb.link
                        (from_page, to_page) VALUES (%s, %s) 
                        RETURNING * """
        cur.execute(sql_query, (site_id, page_id))
        link = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Inserting link to DB led to", error)
    return link


# POST PAGE_DATA
def insertPageDataToDB(site_id, data_type, db_connection):
    page_data = None
    data_type = data_type[1:]
    data_type_caps = data_type.upper()

    cur = db_connection.cursor()
    try:
        sql_query = """ INSERT into crawldb.page_data (page_id, data_type_code) 
                        VALUES (%s, %s) 
                        RETURNING * """
        cur.execute(sql_query, (site_id, data_type_caps))
        page_data = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Inserting page_data led to", error)
    return page_data


# POST IMAGE
def insertImageDataToDB(site_id, filename, content_type, db_connection):
    now = datetime.now()
    access_time = now.strftime("%Y-%m-%d %H:%M:%S'")
    image = None

    cur = db_connection.cursor()
    try:
        sql_query = """ INSERT into crawldb.image (page_id, filename, content_type, accessed_time) 
                        VALUES (%s, %s, %s, %s) 
                        RETURNING * """
        cur.execute(
            sql_query, (site_id, filename, content_type, access_time))
        image = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Inserting image led to", error)
    return image
