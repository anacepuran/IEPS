import os
import sys
import time
import sqlite3
from preprocess import process_text, process_query
from printout import print_snippet, print_table_header, print_query


results = {}


def run_sqlite_search(query):
    conn = sqlite3.connect('inverted-index.db')
    c = conn.cursor()
    sql = '''    
        SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs
        FROM Posting p
        WHERE
            p.word IN ({seq})
        GROUP BY p.documentName
        ORDER BY freq DESC;'''.format(seq=','.join(['?']*len(query)))
    cursor = c.execute(sql, query)

    for row in cursor:

        path = '../input/' + row[0]

        with open(path, "r", encoding='utf8', errors='ignore') as f:
            html = f.read()
            words = process_text(html)
            indexes = [int(s) for s in row[2].split(',')]
            snippet = print_snippet(words, indexes)
            print("%d\t\t %s\t\t\t%s" % (row[1], row[0], snippet))


if __name__ == '__main__':

    input_args = sys.argv[1:]

    params = " ".join(input_args)

    print_query(params)

    processed_query = process_query(params)

    print_table_header()

    start_time = time.time()

    run_sqlite_search(processed_query)

    print("\n\nCompleted in %s seconds." % (time.time() - start_time))
