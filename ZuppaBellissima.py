import json

from bs4 import BeautifulSoup
import requests


def get_url_html(url):
    print(url)
    result = requests.get(url)
    doc = BeautifulSoup(result.text, 'html.parser')

    tags = doc.find_all(class_='price')
    for tag in tags:
        print(tag)

    print()
    print('-----------------------')
    print()


def get_url_array(json_):
    if 'sites' in json_:
        if 'authorized' in json_['sites']:
            if 'authorized' in json_['sites']:
                return json_['sites']
    else:
        raise Exception('Json non valido')


if __name__ == '__main__':
    with open('fake_ecommerce.json', 'r') as f:
        str = f.read()
        sites = get_url_array(json.loads(str))

    for url in sites['authorized']:
        try:
            get_url_html(url)
        except Exception:
            print(f'Error on {url}')