import json
import os
import glob
import re
import socket
import geocoder

from bs4 import BeautifulSoup
import requests


def check_redirects(url):
    try:
        r = requests.get(url, allow_redirects=False, timeout=10)
        redirect = r.headers['location']
        return redirect if 'http' in redirect else url
    except:
        return url


def get_url_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    result = requests.get(url, headers=headers, timeout=10).content
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
            print(f'---------------------------\nStarting {url}')
            redirect = check_redirects(url)
            print(f'Reditecting to {redirect}')
            path = f'{class_folder}' \
                   f'{redirect.replace("http://", "http-").replace("https://", "https-").split("/")[0]}.html'
            try:
                with open(path, 'w', encoding='utf-8') as class_file:
                    doc = get_url_html(redirect)
                    if not doc.find('head'):
                        raise Exception('<head> not found')
                    title = doc.find('title').text
                    if 'Error' in title:
                        raise Exception('HTML Error')
                    if 'Not Found' in title:
                        raise Exception('Not Found')
                    if 'Kaspersky Security Cloud' in title:
                        raise Exception('Security Error')
                    if 'Access Denied' in title:
                        raise Exception('Access Denied')
                    if 'Cloudflare' in title:
                        raise Exception('Blocked by Cloudflare')
                    class_file.write(str(doc))
                    print(f'{redirect} Successful')
            except Exception as e:
                print(f'Error on {redirect} --- {e}')
                os.remove(path)


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

# TODO
def feature_p_iva(doc):
    return url if 'iva' in doc.text.lower() else ''

# TODO
def feature_login_btn(doc):
    tmp = []
    try:
        found = doc.find_all('a')
        for tag in found:
            if 'login' in tag['href'].lower() or 'sign in' in tag['href'].lower():
                tmp.append(url)
                break
    finally:
        return tmp

# TODO
def feature_payment_methods(doc):
    tmp = 0
    try:
        found = doc.find_all('img')
        tmp = 1 if any('card' in tag['class'] for tag in found) else 0
    finally:
        return tmp


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
            ciao = check_redirects(url)
            if ciao:
                print(ciao)
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
                       f'{feature_social_link(doc, social="pinterest")};' \
                       f'\n'

    with open('Stats/total.csv', 'w+') as stats:
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
                    'pinterest;'
                    '\n')
        stats.write(tmp_csv)

