import psycopg2
from psycopg2 import pool
from crawler.URLfrontier import processSeedPages

db = {
    'host': 'localhost',
    'port': '5432',
    'db_name': 'spider',
    'username': 'postgres',
    'password': 'modronebo.12'
}
db_pool = None


def initiateConnectionToDatabase(seed_urls, domains):
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
    sql_query = "SELECT * FROM crawldb.site LIMIT 1"
    cur.execute(sql_query)
    current_page = cur.fetchone()
    print("Current URL in frontier: ", current_page)

    if not current_page:
        processSeedPages(seed_urls, domains, db_connection)


def closeConnectionToDatabase():
    try:
        if db_pool:
            db_pool.closeall()
            print('PostgreSQL connection pool is closed!')
    except Exception as error:
        print(error)
