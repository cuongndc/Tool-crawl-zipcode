import requests
# import urllib.request
# import time
from bs4 import BeautifulSoup
import json
import os
#
# # Set the URL you want to webscrape from
# url = 'http://www.gpspostcode.com/zip-code/germany/freiburg/'
#
# # Connect to the URL
# response = requests.get(url)
#
# # Parse HTML and save to BeautifulSoup object¶
# soup = BeautifulSoup(response.text, 'html.parser')
#
# rows = soup.find_all("tr")
# headrow = rows[1]
# datarows = rows[1:]
#
# for num, h in enumerate(headrow):
#     print('num', num)
#     print("h", h)
#     for row in datarows:
#         print('row', row.find('td'))
#
#     # data = ", ".join([row[num].text for row in datarows])
#     # print("{0:<16}: {1}".format(h.text, data))
#
# # # Search table
# # tables = soup.find_all('table', class_='table_milieu')
# #
# # datasets = []
# # # for table in tables:
# #     # The first tr contains the field names.
# # headings = [th.get_text().strip() for th in tables[1].find("tr").find_all("th")]
# # print(headings)
# #
# # for row in tables[1].find_all("tr")[1:]:
# #     for td in row.find_all("td"):
# #         # print("td", td.get_text())
# #         dataset = {
# #             'xxx': td.get_text()
# #         }
# #         datasets.append(dataset)
# #
# # print(datasets)
#

from html_table_extractor.extractor import Extractor

# Set the URL you want to webscrape from
# url = 'http://www.gpspostcode.com/zip-code/germany/freiburg/'

url_file = 'url.json'
f = open(url_file, )
# returns JSON object as
# a dictionary
list_url = json.load(f)
# Iterating through the json

href_state = []
for u in list_url:
    # Connect to the URL
    res = requests.get(u['url'])
    if res.text is None:
        continue

    soup = BeautifulSoup(res.text, 'html.parser')
    for a in soup.find_all('a', href=True, text=True):
        state_name = a.get_text()
        href = a['href']
        if 'www' in href:
            result = {
                'country_code': u['country_code'],
                'url': href
            }
            url_file = 'source/' + u['country_code'] + '.json'
            f = open(url_file, )
            # returns JSON object as
            # a dictionary
            state = json.load(f)
            for s in state:
                if state_name == s['name']:
                    result['state_code'] = s['code']
                    result['state_name'] = s['name']

            href_state.append(result)


href_district = []
for href_s in href_state:
    res = requests.get(href_s['url'])
    if res.text is None:
        continue

    soup = BeautifulSoup(res.text, 'html.parser')
    for a in soup.find_all('a', href=True, text=True):
        href = a['href']
        if 'www' in href:
            result = {
                'url': href,
                'country_code': href_s['country_code'],
                'state_code': href_s['state_code'],
                'state_name': href_s['state_name']
            }

            href_district.append(result)

count = 0
for district in href_district:
    print('district', district)
    result = None
    res = requests.get(district['url'])
    soup = BeautifulSoup(res.text, 'html.parser')

    tables = soup.find_all('table')
    for table in tables:
        extractor = Extractor(table, class_='table_milieu')
        extractor.parse()
        result = extractor.return_list()

    query = ''
    for num, re in enumerate(result):
        city = re[2] if re[2] is not None else ''
        if city is not None and city != 'City':
            state = district['state_name'] if district['state_name'] is not None else ''
            zip_code = re[1] if re[1] is not None else ''
            state_code = district['state_code'] if district['state_code'] is not None else ''
            country_code = district['country_code'] if district['country_code'] is not None else ''
            query += 'insert into checkout.zip_code (CITY, COUNTRY_CODE, ZIP_CODE, STATE_CODE, STATE) VALUES' + '(' + "'" + city + "'" + ',' + "'" + country_code + "'" + ',' + "'" + zip_code + "'" + ',' + "'" + state_code + "'" + ',' + "'" + state + "'" + '); \n'
            count += 1
            print('count', count)
#
#
    write_path = 'output/' + country_code + state_code + '.sql'
    mode = 'a' if os.path.exists(write_path) else 'w'
    with open(write_path, mode) as f:
        f.write(query)
