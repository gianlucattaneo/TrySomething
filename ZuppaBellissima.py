import json
import os

from bs4 import BeautifulSoup
import requests


def get_url_html(url):
    result = requests.get(url)
    onl = BeautifulSoup(result.text, 'html.parser')
    return onl


def get_url_html_offline(url,class_):
    with open(f'Html/{class_}/{url.replace("http://", "").replace("https://", "")}.html', 'r', encoding="utf8") as f:
        off = BeautifulSoup(f, 'html.parser')
    return off


def get_url_array(json_):
    if 'sites' in json_:
        if 'authorized' in json_['sites']:
            if 'authorized' in json_['sites']:
                return json_['sites']
    else:
        raise Exception('Json non valido')


if __name__ == '__main__':
    with open('fake_ecommerce.json', 'r') as f:
        content = f.read()
        sites = get_url_array(json.loads(content))

    feature = 'meta'

    class_folder = 'Stats/'
    os.makedirs(class_folder, exist_ok=True)
    classes = ['authorized', 'unauthorized']
    with open(f'{class_folder}{feature}.csv', 'w') as class_file:
        class_file.write(f'url;class;{feature}_count\n')
        for class_ in classes:
            for url in sites[class_]:
                try:
                    doc = get_url_html_offline(url, class_)
                    found = doc.findAll(feature)
                    class_file.write(f'{url};{class_};{len(found)}\n')
                    # class_file.write(f'{url};{class_};{1 if "https" in url else 0}\n')
                except Exception as e:
                    print(f'Error on {url} -- {e}')

    # folder = 'Html/'
    # classes = ['authorized', 'unauthorized']
    # for class_ in classes:
    #     class_folder = f'{folder}{class_}/'
    #     os.makedirs(class_folder, exist_ok=True)
    #     for url in sites[class_]:
    #         try:
    #             with open(f'{class_folder}'
    #                       f'{url.replace("http://", "").replace("https://", "")}.html',
    #                       'w',
    #                       encoding='utf-8') as class_file:
    #                 class_file.write(str(get_url_html(url)))
    #         except Exception as e:
    #             print(f'Error on {url}')
