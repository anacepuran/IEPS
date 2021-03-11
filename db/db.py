import psycopg2
from psycopg2 import pool
from datetime import datetime

db = {
    'host': 'localhost',
    'port': '5432',
    'db_name': 'spider',
    'username': 'postgres',
    'password': 'postgres'
}
db_pool = None


def initiateConnectionToDatabase(seed_urls):
    # initiate connection
    try:
        db_pool = pool.ThreadedConnectionPool(3, 10, user=db['username'], password=db['password'],
                                              host=db['host'], port=db['port'], database=db['db_name'])
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
    print("Current URL in frontier: ", current_page)

    return [current_page, db_connection]


def closeConnectionToDatabase():
    try:
        if db_pool:
            db_pool.closeall()
            print('PostgreSQL connection pool is closed!')
    except Exception as error:
        print("Closing the database connection led to", error)


# POST SITE
def insertSiteToDB(url, response_robots, sitemap, db_connection):
    site_id = None
    cur = db_connection.cursor()
    try:
        sql_query = """ INSERT into crawldb.site (domain, robots_content, sitemap_content) 
                        VALUES (%s, %s, %s) 
                        RETURNING id """
        cur.execute(sql_query, (url, response_robots, sitemap))
        site_id = cur.fetchone()[0]
        db_connection.commit()
    except Exception as error:
        print("Inserting the site to the database led to", error)
    return site_id


# GET FIRST UNPROCESSED PAGE
def getFirstFromFrontier(db_connection):
    cur = db_connection.cursor()
    accessed_current_page = None

    try:
        sql_query = """ SELECT * FROM crawldb.page 
                        WHERE accessed_time IS NULL
                        LIMIT 1 """
        cur.execute(sql_query)
        current_page = cur.fetchone()
        print(current_page)
        if current_page is not None:
            now = datetime.now()
            access_time = now.strftime("%Y-%m-%d %H:%M:%S'")

            sql_query = """ UPDATE crawldb.page
                            SET accessed_time = %s
                            WHERE id = %s 
                            RETURNING * """
            cur.execute(sql_query, (access_time, current_page[0]))
            print(accessed_current_page)
            accessed_current_page = cur.fetchone()
            db_connection.commit()
    except Exception as error:
        print("Getting the first site from the frontier led to", error)
    return accessed_current_page


# POST PAGE
def insertPageToDB(url, site_id, db_connection):
    page_id = None
    cur = db_connection.cursor()

    try:
        sql_query = """ INSERT into crawldb.page (site_id, url) 
                        VALUES (%s, %s) 
                        RETURNING id """
        cur.execute(sql_query, (site_id, url))
        page_id = cur.fetchone()[0]
        db_connection.commit()
    except Exception as error:
        print("Inserting the page to the frontier led to", error)
    return page_id


# PUT PAGE - DUPLICATE
def updatePageAsDuplicate(current_page, duplicate, db_connection):
    page_type_code = "DUPLICATE"
    html_content = "NULL"
    to_page = duplicate[0]
    from_page = current_page[0]
    try:
        sql_query = """ UPDATE crawldb.page
                        SET page_type_code = %s, html_content = %s
                        WHERE id = %s 
                        RETURNING * """
        cur.execute(sql_query, (page_type_code, html_content, from_page))
        duplicate_page = cur.fetchone()
        sql_query = """ INSERT INTO crawldb.link
                        (from_page, to_page) VALUES (%s, %s) """
        cur.execute(sql_query, (from_page, to_page))
        duplicate_link = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Updating page as duplicate in frontier led to", error)
    return duplicate_page


# PUT PAGE - INACCESSIBLE
def updatePageAsInaccessible(current_page, http_status_code, db_connection):
    page_type_code = "HTML"
    html_content = "NULL"
    try:
        sql_query = """ UPDATE crawldb.page
                        SET page_type_code = %s, html_content = %s, http_status_code = %s
                        WHERE id = %s 
                        RETURNING * """
        cur.execute(sql_query, (page_type_code, html_content,
                                http_status_code, current_page[0]))
        inaccessible_page = cur.fetchone()
        db_connection.commit()
    except Exception as error:
        print("Updating page as inaccessible in frontier led to", error)
    return inaccessible_page


# PUT PAGE - INACCESSIBLE
def updatePageAsBinary(current_page, db_connection):
    return 0


# POST PAGE DATA
def insertPageDataToDB(current_page, db_connection):
    return 0
