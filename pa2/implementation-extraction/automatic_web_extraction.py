import codecs
from html.parser import HTMLParser
from lxml.html.clean import Cleaner
import sys

parsed_tokens = []


def clean_file(file):

    cleaner = Cleaner()

    cleaner.javascript = True  # This is True because we want to activate the javascript filter
    cleaner.style = True  # This is True because we want to activate the styles & stylesheet filter
    cleaner.kill_tags = ['head', 'img', 'iframe', 'nav', 'svg', 'figure', 'map']

    file = cleaner.clean_html(file)

    file = file.split()
    file = " ".join(file)

    # print(file)

    return file


class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        parsed_tokens.append(["s_tag", tag])
        # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        parsed_tokens.append(["e_tag", tag])
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        if data != ' ':
            parsed_tokens.append(["data", data])
        # print("Encountered some data  :", data)


def final_wrapper_ufre(wrapper):

    ufre = ""

    for token in wrapper:
        
        tag = ""

        if token[0] == "s_tag":
            tag += "".join(["<", token[1], ">\n"])

        elif token[0] == "e_tag":
            tag += "".join(["</", token[1], ">\n"])

        elif token[0] == "optional":
            tag += token[1] + "\n"

        else:
            tag += token[1] + "\n"

        ufre += tag

    return ufre


def match_found(t1, t2):
    if t1[0] == t2[0] and t1[1] == t2[1]:
        return True
    else:
        return False


def roadrunner(p1_tokens, p2_tokens, w, s, wrapper):

    """ END OF HTML FILE(S) """
    if w == len(p1_tokens) and s == len(p2_tokens):
        return wrapper

    p1_token = p1_tokens[w]
    p2_token = p2_tokens[s]

    """ MATCHING TOKENS """
    if match_found(p1_token, p2_token):
        wrapper.append(p1_token)
        return roadrunner(p1_tokens, p2_tokens, w + 1, s + 1, wrapper)

    """ FOUND DATA """
    if p1_token[0] == "data" and p2_token[0] == "data":
        wrapper.append(["data", "#PCDATA"])
        return roadrunner(p1_tokens, p2_tokens, w + 1, s + 1, wrapper)

    else:
        return wrapper



def awe():

    """ READ INPUT FILES """

    file_overstock_1 = codecs.open("../input-extraction/overstock.com/jewelry01.html", "r", "ISO-8859-1")
    file_overstock_2 = codecs.open("../input-extraction/overstock.com/jewelry02.html", "r", "ISO-8859-1")

    file_rtv_1 = codecs.open(
        "../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r",
        "utf-8")
    file_rtv_2 = codecs.open(
        "../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
        "r", "utf-8")

    file_avtonet_1 = codecs.open("../input-extraction/avto.net/www.Avto.net_ Največja ponudba.html", "r",
                                 "windows-1250")
    file_avtonet_2 = codecs.open("../input-extraction/avto.net/www.Avto.net_ Največja ponudba_2.html", "r",
                                 "windows-1250")

    page1 = clean_file(file_overstock_1.read())
    page2 = clean_file(file_overstock_2.read())

    page1 = clean_file(file_rtv_1.read())
    page2 = clean_file(file_rtv_2.read())

    page1 = clean_file(file_avtonet_1.read())
    page2 = clean_file(file_avtonet_2.read())

    parser = MyHTMLParser()

    """ GET TOKENS """
    parser.feed(page1)
    p1_tokens = list(parsed_tokens)
    print(p1_tokens)
    parsed_tokens.clear()
    parser.feed(page2)
    p2_tokens = list(parsed_tokens)
    print(p2_tokens)

    """ RUN ROADRUNNER """
    final_wrapper = roadrunner(p1_tokens, p2_tokens, 0, 0, [])

    ufre = final_wrapper_ufre(final_wrapper)
    print(ufre)


if __name__ == "__main__":

    # print(sys.getrecursionlimit())
    sys.setrecursionlimit(2000)
    # read_files()

