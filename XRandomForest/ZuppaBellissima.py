import json
import os
import glob
import re
import socket
import traceback

import geocoder
import time

from bs4 import BeautifulSoup
import requests


def check_redirects(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }

    try:
        r = requests.get(url, headers=headers, timeout=25)
    except Exception as e:
        raise Exception(str(type(e)))

    for redirect in r.history:
        print(redirect.url, redirect.status_code)

    if r.status_code != 200:
        raise Exception(f'Errore HTML {r.status_code} su {r.url}')

    doc = BeautifulSoup(r.content, 'html.parser')
    return r.url, doc


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


def save_html(classes, sites, folder='../Html/'):
    original_names = ''
    for class_ in classes:
        class_folder = f'{folder}{class_}/'
        os.makedirs(class_folder, exist_ok=True)
        for url in sites[class_]:
            print(f'---------------------------\nStarting {url}')
            try:
                redirect, doc = check_redirects(url)
            except Exception as e:
                print(e.args)
                continue

            original_names += f'{url};{redirect}\n'

            formatted = redirect.replace("http://", "http-") \
                .replace("https://", "https-") \
                .split("/")[0] \
                .split("?")[0] \
                .split(":")[0]

            path = f'{class_folder}{formatted}.html'
            with open(path, 'w', encoding='utf-8') as class_file:
                class_file.write(str(doc))
                print(f'{redirect} Successful')
    with open('../res/original_names.csv', 'w') as file:
        file.write('original;redirect\n')
        file.write(original_names)


def feature_https(url):
    return 1 if "https" in url else 0


def feature_meta_count(doc):
    found = doc.find_all('meta')
    return len(found) if found else 0


def feature_url_length(url):
    split = url.split('//')[1].split('.')
    return len(split[1] if 'www' in url else split[0])


def feature_google_verified(doc):
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
        return len(glob_domains) - 1


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


# # TODO
# def feature_p_iva(doc):
#     return url if 'iva' in doc.text.lower() else ''
#
# # TODO
# def feature_login_btn(doc):
#     tmp = []
#     try:
#         found = doc.find_all('a')
#         for tag in found:
#             if 'login' in tag['href'].lower() or 'sign in' in tag['href'].lower():
#                 tmp.append(url)
#                 break
#     finally:
#         return tmp
#
# # TODO
# def feature_payment_methods(doc):
#     tmp = 0
#     try:
#         found = doc.find_all('img')
#         tmp = 1 if any('card' in tag['class'] for tag in found) else 0
#     finally:
#         return tmp


def feature_ip_location(url):
    try:
        ip = socket.gethostbyname(url.replace('http://', '').replace('https://', '').replace('www.', ''))
        request_url = 'https://geolocation-db.com/jsonp/' + ip
        response = requests.get(request_url)
        result = response.content.decode()
        result = result.split("(")[1].strip(")")
        loc = json.loads(result)['country_code']
        # loc = geocoder.ip(ip)
        if loc in glob_country_codes:
            return glob_country_codes.index(loc)
        else:
            glob_country_codes.append(loc)
            return len(glob_country_codes) - 1
    except:
        return 0


def feature_trustpilot_review(url):
    try:
        url = url.replace('http://', '').replace('https://', '')
        request_url = 'https://www.trustpilot.com/review/' + url
        response = requests.get(request_url).content
        doc = BeautifulSoup(response, 'html.parser').find('p', {'data-rating-typography': True}).text
        return doc
    except:
        return -1.0


def feature_social_link(doc, social):
    found = doc.find_all('a')
    for tag in found:
        try:
            if social in tag['href']:
                return 1
        except:
            pass
    return 0


glob_country_codes = ['Not found']
glob_domains = []

if __name__ == '__main__':
    with open('res/bilanciato_v2.json', 'r') as f:
        content = f.read()
        sites = get_url_array(json.loads(content))
    save_html(['authorized', 'unauthorized'], sites)

    classes = ['authorized', 'unauthorized']
    sites = {}
    for class_ in classes:
        tmp = []
        for pseudo_url in glob.glob(f'../Html/{class_}/*.html'):
            url = pseudo_url.replace('http-', 'http://')\
                .replace('https-', 'https://')\
                .replace('.html', '')\
                .split('\\')[1]
            tmp.append(url)
        sites[class_] = tmp

    tmp_csv = ''
    for class_ in sites:
        for url in sites[class_]:
            doc = get_url_html_offline(url, class_)
            tmp_csv += f'{url};{class_};' \
                       f'{feature_https(url)};' \
                       f'{feature_meta_count(doc)};'\
                       f'{feature_url_length(url)};' \
                       f'{feature_google_verified(doc)};' \
                       f'{feature_domain(url)};' \
                       f'{feature_url_numbers(url)};' \
                       f'{feature_url_special_chars(url)};' \
                       f'{feature_ip_location(url)};' \
                       f'{feature_trustpilot_review(url)};' \
                       f'{feature_social_link(doc, social="instagram")};' \
                       f'{feature_social_link(doc, social="facebook")};'\
                       f'{feature_social_link(doc, social="twitter")};' \
                       f'{feature_social_link(doc, social="pinterest")}' \
                       f'\n'
            print(f'{url} - Done')

    with open('../Stats/total.csv', 'w+') as stats:
        # TODO ricordarsi di aggiungere i campi
        stats.write('url;class;https;'
                    'meta_count;'
                    'url_length;'
                    'google_verified;'
                    'domain;'
                    'url_numbers;'
                    'special_chars;'
                    'ip_location;'
                    'trustpilot_review;'
                    'instagram;'
                    'facebook;'
                    'twitter;'
                    'pinterest'
                    '\n')
        stats.write(tmp_csv)

