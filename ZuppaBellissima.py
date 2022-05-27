import json
import os
import glob
import re

from bs4 import BeautifulSoup
import requests


def get_url_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    result = requests.get(url, headers=headers).content
    onl = BeautifulSoup(result, 'html.parser')
    return onl


def get_url_html_offline(url, class_):
    with open(f'Html/{class_}/{url.replace("http://", "http-").replace("https://", "https-")}.html',
              'r', encoding="utf8") as html_text:
        off = BeautifulSoup(html_text, 'html.parser')
    return off


def get_url_array(json_):
    if 'sites' in json_:
        if 'authorized' in json_['sites']:
            if 'authorized' in json_['sites']:
                return json_['sites']
    else:
        raise Exception('Json non valido')


def save_html(classes, sites, folder='Html/'):
    for class_ in classes:
        class_folder = f'{folder}{class_}/'
        os.makedirs(class_folder, exist_ok=True)
        for url in sites[class_]:
            path = f'{class_folder}{url.replace("http://", "http-").replace("https://", "https-")}.html'
            try:
                with open(path, 'w', encoding='utf-8') as class_file:
                    doc = get_url_html(url)
                    if not doc.find('head'):
                        raise Exception('<head> not found')
                    title = doc.find('title').text
                    if 'Error' in title:
                        raise Exception('HTML Error')
                    if 'Kaspersky Security Cloud' in title:
                        raise Exception('Security Error')
                    if 'Access Denied' in title:
                        raise Exception('Access Denied')
                    class_file.write(str(doc))
            except Exception as e:
                print(f'Error on {url} --- {e}')
                os.remove(path)


def vecchio():
    with open('fake_ecommerce.json.json', 'a') as f:
        content = f.read()
        sites = get_url_array(json.loads(content))

    classes = ['authorized', 'unauthorized']
    # save_html(classes, sites)

    feature = 'len_url'
    class_folder = 'Stats/'
    os.makedirs(class_folder, exist_ok=True)
    with open(f'{class_folder}{feature}.csv', 'w') as class_file:
        class_file.write(f'{feature}\n')
        for class_ in classes:
            for url in sites[class_]:
                try:

                    if 'www' in url:
                        print(url.split('.')[1])
                    else:
                        print(url.split('.')[0])
                    # class_file.write(f'{url};{class_};'
                    #                  f'{1 if "https" in url else 0}\n')
                    # doc = get_url_html_offline(url, class_)
                    # found = doc.find('head')

                    # if found:
                    #     # found = found.find_all('meta', {'name': 'google-site-verification'})
                    #     class_file.write('1\n')
                    # else:
                    #     class_file.write('0\n')

                except Exception as e:
                    print(f'Error on {url} -- {e}')


def feature_https(url):
    return 1 if "https" in url else 0


def feature_meta_count(url, class_):
    doc = get_url_html_offline(url, class_)
    found = doc.find_all('meta')
    return len(found) if found else 0


def feature_url_length(url):
    split = url.split('//')[1].split('.')
    return len(split[1] if 'www' in url else split[0])


def feature_google_verified(url, class_):
    doc = get_url_html_offline(url, class_)
    found = []
    try:
        found = doc.find('head').find_all('meta', {'name': 'google-site-verification'})
    finally:
        return len(found)


def feature_domain(url):
    domain = url.replace('.html', '').split('.')[-1]
    if domain in glob_domains:
        # print(domain, glob_domains.index(domain))
        return glob_domains.index(domain)
    else:
        glob_domains.append(domain)
        # print(domain, len(glob_domains)-1)
        return len(glob_domains)-1


def feature_url_numbers(url):
    split = url.split('.')
    truncated = split[1] if 'www' in url else split[0]
    # print(1 if any(char.isdigit() for char in truncated) else 0, truncated)
    return 1 if any(char.isdigit() for char in truncated) else 0


def feature_url_special_chars(url):
    regex = re.compile('[@_!#$%^&*()<>?/}{~:\-|]')
    split = url.split('.')
    truncated = split[1] if 'www' in url else split[0].split('//')[1]
    return 1 if regex.search(truncated) else 0


def feature_p_iva(url, class_):
    doc = get_url_html_offline(url, class_)
    return url if 'iva' in doc.text.lower() else ''


def feature_login_btn(url, class_):
    doc = get_url_html_offline(url, class_)
    found = []
    tmp = []
    try:
        found = doc.find_all('a')
        for tag in found:
            if 'login' in tag['href'].lower() or 'sign in' in tag['href'].lower():
                tmp.append(url)
                break
    finally:
        return tmp


glob_domains = []

if __name__ == '__main__':
    # with open('fake_ecommerce.json', 'r') as f:
    #     content = f.read()
    #     sites = get_url_array(json.loads(content))
    # save_html(['authorized', 'unauthorized'], sites)

    classes = ['authorized', 'unauthorized']
    sites = {}
    for class_ in classes:
        tmp = []
        for pseudo_url in glob.glob(f'Html/{class_}/*.html'):
            url = pseudo_url.replace('http-', 'http://')\
                .replace('https-', 'https://')\
                .replace('.html', '')\
                .split('\\')[1]
            tmp.append(url)
        sites[class_] = tmp

    tmp_csv = ''
    for class_ in sites:
        for url in sites[class_]:
            print(feature_p_iva(url, class_))
            # tmp_csv += f'{url};{class_};' \
            #            f'{feature_https(url)};' \
            #            f'{feature_meta_count(url,class_)};'\
            #            f'{feature_url_length(url)};' \
            #            f'{feature_google_verified(url,class_)};' \
            #            f'{feature_domain(url)};' \
            #            f'{feature_url_numbers(url)};' \
            #            f'{feature_url_special_chars(url)}\n'

    # with open('Stats/total.csv', 'w') as stats:
    #     # TODO ricordarsi di aggiungere i campi
    #     stats.write('url;class;https;meta_count;url_length;google_verified;domain;url_numbers;special_chars\n')
    #     stats.write(tmp_csv)

