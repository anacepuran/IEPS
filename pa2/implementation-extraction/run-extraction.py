import codecs
import sys
import io

from regex import regex_overstock, regex_rtvslo, regex_avtonet
from xpath import xpath_overstock, xpath_rtvslo, xpath_avtonet
from automatic_web_extraction import awe


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

    file_avtonet_1 = codecs.open("../input-extraction/avto.net/www.Avto.net_ Največja ponudba.html", "r", "windows-1250")
    file_avtonet_2 = codecs.open("../input-extraction/avto.net/www.Avto.net_ Zadnjih 100.html", "r", "windows-1250")

    files_overstock.append(file_overstock_1.read())
    files_overstock.append(file_overstock_2.read())

    files_rtvslo.append(file_rtv_1.read())
    files_rtvslo.append(file_rtv_2.read())

    files_avtonet.append(file_avtonet_1.read())
    files_avtonet.append(file_avtonet_2.read())


def hello(method):

    if method == 'A':
        regular_expressions()

    elif method == 'B':
        xpath()

    elif method == 'C':
        automatic_web_extraction()

    else:
        print("Please provide a valid parameter.")


def regular_expressions():
    regex_overstock(files_overstock)
    regex_rtvslo(files_rtvslo)
    regex_avtonet(files_avtonet)


def xpath():
    xpath_overstock(files_overstock)
    xpath_rtvslo(files_rtvslo)
    xpath_avtonet(files_avtonet)


def automatic_web_extraction():
    awe()


if __name__ == "__main__":
    param = sys.argv[1]
    get_files()
    hello(param)

