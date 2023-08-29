import time
from selenium import webdriver
from models import *


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--blink-settings=imagesEnabled=false')
    # options.add_argument('--headless')
    options.add_argument('--window-size=1440,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')  # run Chrome use root
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"')
    driver = webdriver.Chrome(options=options)
    return driver


def get_data(driver, keys, main_key):
    href_list = []
    for p in range(1, 102):
        url = f'https://www.yellowpages.com/search?search_terms={main_key}&geo_location_terms={keys}&page={p}'
        source = keys + ' ' + main_key
        driver.get(url)
        time.sleep(5)
        hl = driver.find_elements_by_css_selector("[class='search-results organic']")
        if hl:
            href_list = hl[0].find_elements_by_class_name("result")
        ss = []
        for i in href_list:
            try:
                name = i.find_element_by_css_selector(".business-name > span").text
            except:
                name = ""
            try:
                phone = i.find_element_by_css_selector("[class='phones phone primary']").text
            except:
                phone = ""
            try:
                address1 = i.find_element_by_css_selector(
                    "[class='info-section info-secondary']").find_element_by_class_name("street-address").text
                address2 = i.find_element_by_css_selector(
                    "[class='info-section info-secondary']").find_element_by_class_name("locality").text
                address = address1 + address2
            except:
                address = ""
            try:
                website = i.find_element_by_class_name('business-name').get_attribute("href")
            except:
                website = ""
            ss.append(
                    dict(name=name, website=website, phone=phone, address=address, groups='yellowpages', source=source))

        for l in ss:
            find_data = SQLsession.query(Infos).filter_by(name=l['name'], groups='yellowpages').first()
            if not find_data:
                SQLsession.add(Infos(**l))
        SQLsession.commit()



if __name__ == '__main__':
    main_key = ['Wigs & Hair Pieces', 'hair extension', 'hair bundle', 'wig salon', 'wig store', 'wig']
    keys_list = read_txt()
    driver = get_driver()
    breaklocation = ''
    for mk in main_key:
        for k in keys_list:
            if breaklocation == k or not breaklocation:
                get_data(driver, k, mk)
                breaklocation = ''
                print(mk + '___' + k)
