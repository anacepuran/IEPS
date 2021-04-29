from lxml import etree


def xpath_overstock(files):

    for file in files:

        dom = etree.HTML(file)

        data = []

        i = 1

        overstock_xpath_title = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/' \
                                'tr[' + str(i) + ']/td[2]/a/b/text()'
        overstock_xpath_content = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
            i) + ']/td[2]/table/tbody/tr/td[2]/span/text()'
        overstock_xpath_list_price = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
            i) + ']/td[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()'
        overstock_xpath_price = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
            i) + ']/td[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()'
        overstock_xpath_saving = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
            i) + ']/td[2]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()'

        while dom.xpath(overstock_xpath_title):

            item_title = dom.xpath(overstock_xpath_title)
            item_content = dom.xpath(overstock_xpath_content)
            item_list_price = dom.xpath(overstock_xpath_list_price)
            item_price = dom.xpath(overstock_xpath_price)
            item_saving = dom.xpath(overstock_xpath_saving)
            item_content = str(item_content[0]).replace("\n", " ")

            tmp = item_saving[0].split()
            item_saving_mny = tmp[0]
            item_saving_prcnt = tmp[1].strip('()')

            data_el = {
                "title": item_title[0],
                "content": item_content,
                "list_price": item_list_price[0],
                "price": item_price[0],
                "item_saving": item_saving_mny,
                "item_saving_percent": item_saving_prcnt
            }

            data.append(data_el)

            if (dom.xpath(
                    '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
                        i + 1) + ']/td/table/tbody/tr[1]/td/span/b')):
                i += 3
            else:
                i += 2

            overstock_xpath_title = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
                i) + ']/td[2]/a/b/text()'
            overstock_xpath_content = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
                i) + ']/td[2]/table/tbody/tr/td[2]/span/text()'
            overstock_xpath_list_price = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
                i) + ']/td[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()'
            overstock_xpath_price = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
                i) + ']/td[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()'
            overstock_xpath_saving = '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[' + str(
                i) + ']/td[2]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()'

        print(data)


def xpath_rtvslo(files):

    for file in files:

        dom = etree.HTML(file)

        item_author = dom.xpath('//*[@id="main-container"]/div[3]/div/header/div[3]/div[1]/strong/text()')
        item_published_time = dom.xpath('//*[@id="main-container"]/div[3]/div/header/div[3]/div[1]/text()')
        item_title = dom.xpath('//*[@id="main-container"]/div[3]/div/header/h1/text()')
        item_subtitle = dom.xpath('//*[@id="main-container"]/div[3]/div/header/div[2]/text()')
        item_lead = dom.xpath('//*[@id="main-container"]/div[3]/div/header/p/text()')
        item_content = dom.xpath('//*[@id="main-container"]/div[3]/div/div[2]/article//p//text()')

        for string in item_content:
            if string == '2':
                index = item_content.index(string)
                item_content[index-1:index+2] = [''.join(item_content[index-1:index+2])]

        item_content = (' '.join(item_content))

        data = {
            "author": item_author[0],
            "published_time": item_published_time[1].strip('| ').replace("\n", "").replace("\t", ""),
            "title": item_title[0],
            "subtitle": item_subtitle[0],
            "lead": item_lead[0],
            "content": item_content
        }

        print(data)


def xpath_avtonet(files):

    for file in files:

        # print("Please wait, there are many results on the page.")

        dom = etree.HTML(file)

        data = []

        i = 2

        title_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[1]/span/text()"
        price_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[6]/div[1]/div[1]/div/text()"
        link_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/a/@href"

        counter = 0

        while counter < 3:

            item_title = dom.xpath(title_xpath)

            if not item_title:
                counter += 1
                pass

            else:
                item_link = dom.xpath(link_xpath)
                item_price = dom.xpath(price_xpath)

                item_first_registration = item_kilometers = item_fuel = item_gearbox = item_engine = ""

                if not item_price:
                    new_price_xpath_1 = "//*[@id=\"results\"]/div[" + str(i) + "]/div[7]/div[1]/div[2]/div[2]/text()"
                    new_price_xpath_2 = "//*[@id=\"results\"]/div[" + str(i) + "]/div[6]/div[1]/div[2]/div[2]/text()"
                    new_price_xpath_3 = "//*[@id=\"results\"]/div[" + str(i) + "]/div[7]/div[1]/div[1]/div/text()"
                    new_price_xpath_4 = "//*[@id=\"results\"]/div[" + str(i) + "]/div[4]/div[3]/div[2]/div[1]/div/text()"
                    if dom.xpath(new_price_xpath_1):
                        item_price = dom.xpath(new_price_xpath_1)
                    elif dom.xpath(new_price_xpath_2):
                        item_price = dom.xpath(new_price_xpath_2)
                    elif dom.xpath(new_price_xpath_3):
                        item_price = dom.xpath(new_price_xpath_3)
                    elif dom.xpath(new_price_xpath_4):
                        item_price = dom.xpath(new_price_xpath_4)

                j = 1

                item_data_field_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[4]/div[1]/div[1]/table/tbody/tr[" + str(j) + "]/td[1]/text()"
                if dom.xpath(item_data_field_xpath):
                    item_data_xpath = "//*[@id=\"results\"]/div[" + str(
                        i) + "]/div[4]/div[1]/div[1]/table/tbody/tr[" + str(
                        j) + "]/td[2]/text()"
                else:
                    item_data_field_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[4]/div/table/tbody/tr[" + str(
                        j) + "]/td[1]/text()"
                    item_data_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[4]/div/table/tbody/tr[" + str(j) + "]/td[2]/text()"

                item_data_field = dom.xpath(item_data_field_xpath)

                while item_data_field:

                    item_data_field = dom.xpath(item_data_field_xpath)

                    if item_data_field:
                        if item_data_field[0] == '1.registracija' or item_data_field[0] == 'Starost':
                            item_first_registration = dom.xpath(item_data_xpath)
                        elif item_data_field[0] == 'Prevoženih':
                            item_kilometers = dom.xpath(item_data_xpath)
                        elif item_data_field[0] == 'Gorivo':
                            item_fuel = dom.xpath(item_data_xpath)
                        elif item_data_field[0] == 'Menjalnik':
                            item_gearbox = dom.xpath(item_data_xpath)
                        elif item_data_field[0] == 'Motor':
                            item_engine = dom.xpath(item_data_xpath)

                    j += 1

                    item_data_field_xpath = "//*[@id=\"results\"]/div[" + str(
                        i) + "]/div[4]/div[1]/div[1]/table/tbody/tr[" + str(j) + "]/td[1]/text()"
                    if dom.xpath(item_data_field_xpath):
                        item_data_xpath = "//*[@id=\"results\"]/div[" + str(
                            i) + "]/div[4]/div[1]/div[1]/table/tbody/tr[" + str(
                            j) + "]/td[2]/text()"
                    else:
                        item_data_field_xpath = "//*[@id=\"results\"]/div[" + str(
                            i) + "]/div[4]/div/table/tbody/tr[" + str(
                            j) + "]/td[1]/text()"
                        item_data_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[4]/div/table/tbody/tr[" + str(
                            j) + "]/td[2]/text()"

                data_el = {
                    "title": item_title[0],
                    "first_registration": item_first_registration[0],
                    "kilometers": str(item_kilometers).strip("[']"),
                    "fuel": item_fuel[0],
                    "gearbox": item_gearbox[0],
                    "engine": item_engine[0].strip(),
                    "price": item_price[0],
                    "link": item_link[0]
                }

                data.append(data_el)

                counter = 0

            i += 1

            title_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[1]/span/text()"
            link_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/a/@href"
            price_xpath = "//*[@id=\"results\"]/div[" + str(i) + "]/div[6]/div[1]/div[1]/div/text()"

        print(data)
