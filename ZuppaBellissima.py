import json
import os

from bs4 import BeautifulSoup
import requests


def get_url_html(url):
    print(url)
    result = requests.get(url)
    doc = BeautifulSoup(result.text, 'html.parser')

    return str(doc)

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

    folder = 'Html/'
    classes = ['authorized', 'unauthorized']
    for class_ in classes:
        class_folder = f'{folder}{class_}/'
        os.makedirs(class_folder, exist_ok=True)
        for url in sites[class_]:
            try:
                with open(f'{class_folder}'
                          f'{url.replace("http://", "").replace("https://", "")}.html',
                          'w') as class_file:
                    class_file.write(get_url_html(url))
            except Exception:
                print(f'Error on {url}')