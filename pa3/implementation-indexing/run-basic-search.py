import sys
import os
import time
from preprocess import process_word, process_text, process_query
from printout import print_snippet, print_table_header, print_query


results = {}


def run_basic_search(query):
    file_index = 0
    directory = '../input'
    for file in os.listdir(directory):
        if file.endswith("html"):
            with open(os.path.join(directory, file), "r", encoding='utf8', errors='ignore') as f:
                html = f.read()
                words = process_text(html)
                frequency = 0
                word_index = 0
                indexes = []
                for word in words:
                    word = process_word(word)
                    if word != "":
                        if word in query:
                            frequency += 1
                            indexes.append(word_index)
                    word_index += 1

            if frequency > 0:
                results[file_index] = [frequency, file, indexes]

            file_index += 1

    sorted_results = sorted(results.values(), key=lambda kv: kv[0], reverse=True)
    get_results(sorted_results)


def get_results(sorted_res):

    for value in sorted_res:
        path = '../input/' + value[1]

        with open(path, "r", encoding='utf8', errors='ignore') as f:
            html = f.read()
            word_list = process_text(html)
            snippet = print_snippet(word_list, value[2])
            print("%d\t\t\t %s\t\t\t\t\t%s" % (value[0], value[1], snippet))


if __name__ == '__main__':
    # get query
    input_args = sys.argv[1:]

    # print query
    params = " ".join(input_args)
    print_query(params)

    # process query
    processed_query = process_query(params)

    print_table_header()

    start_time = time.time()

    run_basic_search(processed_query)

    print("\n\nCompleted in %s seconds." % (time.time() - start_time))
