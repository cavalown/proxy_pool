import sys
sys.path.append(r'/home/cavalown/python_env/proxy_pool')

import requests
from bs4 import BeautifulSoup
from databaseServer import mongoServer as mongo
import time
from write_file import write_to_csv as wcsv
import datetime

# url = 'https://www.us-proxy.org/'
# url = 'https://free-proxy-list.net/'

url_list = ['https://www.us-proxy.org/', 'https://free-proxy-list.net/']
test_ipv4 = 'https://api.ipify.org?format=json'

while True:
    for url in url_list:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            mongoclient = mongo.mongo_connection('linode1', 'mongo')
            mongocollection = mongo.mongo_collection(mongoclient, 'proxy', 'proxyPool_1')
            proxy_table = soup.select('div[class="modal-body"]>textarea[class="form-control"]')
            update_time = '|'.join(proxy_table[0].text.split('\n')[1].split(' ')[2:4])
            proxies = proxy_table[0].text.split('\n')[3:]
            for proxy in proxies:
                # print(proxy)
                ip = proxy.split(':')[0]
                port = proxy.split(':')[1]
                try:
                    res_test = requests.get(test_ipv4, proxies={'https': proxy, 'http': proxy}, timeout=5)
                    doc = {'_id': ip.replace('.', '') + '_' + port,
                           'ip': ip,
                           'port': port,
                           'updateTime': update_time}
                    print(doc)
                    mongo.insert_document(mongocollection, doc)
                except Exception:
                    print(f"{ip}:{port} Fail")
        except Exception as e:
            print(e)
            wcsv.writeToCsv('/home/cavalown/stock_project/proxy/proxy_exception',
                            [datetime.datetime.now(), e])
    time.sleep(900)
