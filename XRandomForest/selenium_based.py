import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import os
import json
import time
import glob
import socket
import requests
import re

chrome_options = Options()

chrome_options.add_argument('log-level=1')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument("user-data-dir=/tmp/chrome_profiles")
chrome_options.add_argument("profile-directory=Profile 1")
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("enable-automation")
chrome_options.page_load_strategy = "eager"
chrome_options.add_argument("--disable-browser-side-navigation")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])


def get_html(driver, url):
    driver.get(url)
    time.sleep(5)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    return html, driver.current_url


def save_html(driver, classes, sites, folder='Html/'):
    for class_ in classes:
        class_folder = f'{folder}{class_}/'
        os.makedirs(class_folder, exist_ok=True)
        for url in sites[class_]:
            try:

                doc, url = get_html(driver, url)

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

                path = f'{class_folder}' \
                       f'{url.replace("http://", "http-").replace("https://", "https-").split("/")[0].split("?")[0]}' \
                       f'.html'

                with open(path, 'w', encoding='utf-8') as class_file:
                    class_file.write(str(doc))
                    print(f'{url} Successful')

            except Exception as e:
                print(f'Error on {url} --- {e}')


def feature_https(url):
    return 1 if "https" in url else 0


def feature_meta_count(driver):
    found = driver.find_elements(by=By.TAG_NAME, value='meta')
    return len(found) if found else 0


def feature_url_length(url):
    split = url.split('//')[1].split('.')
    return len(split[1] if 'www' in url else split[0])


def feature_google_verified(driver):
    found = []
    try:
        # found = doc.find('head').find_all('meta', {'name': 'google-site-verification'})
        driver.find_elements(by=By.NAME, value='google-site-verification')
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


def feature_social_link(driver, social):
    found = driver.find_elements(by=By.TAG_NAME, value='a')
    for tag in found:
        try:
            if social in tag.get_attribute('href'):
                return 1
        except:
            pass
    return 0


glob_country_codes = ['Not found']
glob_domains = []

if __name__ == '__main__':
    driver = webdriver.Remote('http://localhost:4444/wd/hub', options=chrome_options)
    tmp_csv = ''
    with open('res/bilanciato_v2.json', 'r') as f:
        content = f.read()
        sites = json.loads(content)['sites']
    # save_html(driver, ['authorized', 'unauthorized'], sites)
    for class_ in sites:
        for url in sites[class_]:
            try:
                driver.get(url)
                tmp_csv += f'{url};{class_};' \
                           f'{feature_https(url)};' \
                           f'{feature_meta_count(driver)};' \
                           f'{feature_url_length(url)};' \
                           f'{feature_google_verified(driver)};' \
                           f'{feature_domain(url)};' \
                           f'{feature_url_numbers(url)};' \
                           f'{feature_url_special_chars(url)};' \
                           f'{feature_ip_location(url)};' \
                           f'{feature_trustpilot_review(url)};' \
                           f'{feature_social_link(driver, social="instagram")};' \
                           f'{feature_social_link(driver, social="facebook")};' \
                           f'{feature_social_link(driver, social="twitter")};' \
                           f'{feature_social_link(driver, social="pinterest")}' \
                           f'\n'
                print(f'{url} - Done')
            except Exception:
                print(traceback.format_exc())
            finally:
                try:
                    driver.quit()
                except Exception: pass
                driver = webdriver.Remote('http://localhost:4444/wd/hub', options=chrome_options)

with open('Stats/sel_total.csv', 'w+') as stats:
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
