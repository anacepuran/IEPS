def print_query(query):
    print()
    print("Results for a query: \"" + query + "\"")


def print_table_header():
    print()
    print("Frequencies Document                                  Snippet")
    print("----------- ----------------------------------------- "
          "-----------------------------------------------------------")


def print_snippet(words, indexes):
    snippet = ""
    for i in indexes:

        if i + 4 <= len(words):
            add_range = 4
        elif i + 3 <= len(words):
            add_range = 3
        elif i + 2 <= len(words):
            add_range = 2
        elif i + 1 <= len(words):
            add_range = 1
        else:
            add_range = 0

        if i >= 3:
            snippet += "... " + " ".join(words[i - 3:i + add_range]) + " ..."
        elif i == 2:
            snippet += "... " + " ".join(words[i - 2:i + add_range]) + " ..."
        elif i == 1:
            snippet += "... " + " ".join(words[i - 1:i + add_range]) + " ..."
        else:
            snippet += "".join(words[i:i + 3]) + "..."

    snippet = snippet.replace("......", "...")
    snippet = snippet.replace(" ,", ",")
    snippet = snippet.replace(" . ", ". ")
    snippet = snippet.replace("....", "...")

    return snippet
