import codecs
import sys

from regex import regex_overstock, regex_rtvslo
from xpath import xpath_overstock, xpath_rtvslo


files_overstock = []
files_rtvslo = []
files_avtonet = []


def get_files():

    file_overstock_1 = codecs.open("../input-extraction/overstock.com/jewelry01.html", "r", "ISO-8859-1")
    file_overstock_2 = codecs.open("../input-extraction/overstock.com/jewelry02.html", "r", "ISO-8859-1")

    file_rtv_1 = codecs.open(
        "../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r",
        "utf-8")
    file_rtv_2 = codecs.open(
        "../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html",
        "r", "utf-8")

    files_overstock.append(file_overstock_1.read())
    files_overstock.append(file_overstock_2.read())
    files_rtvslo.append(file_rtv_1.read())
    files_rtvslo.append(file_rtv_2.read())


def hello(method):

    if method == 'A':
        regular_expressions()

    elif method == 'B':
        xpath()

    elif method == 'C':
        print("Generation of extraction rules using automatic Web extraction algorithm.")

    else:
        print("Please provide a valid parameter.")


def regular_expressions():
    regex_overstock(files_overstock)
    regex_rtvslo(files_rtvslo)


def xpath():
    xpath_overstock(files_overstock)
    xpath_rtvslo(files_rtvslo)


def automatic_web_extraction():
    print("empty")


if __name__ == "__main__":
    param = sys.argv[1]
    get_files()
    hello(param)

