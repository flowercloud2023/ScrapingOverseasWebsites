import time
from selenium import webdriver
from models import *
import traceback


def wirte_infos(data):
    for d in data:
        find_data = SQLsession.query(Infos).filter_by(name=d['name'], groups='Yelp').first()
        if not find_data:
            SQLsession.add(Infos(**d))
    SQLsession.commit()


def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--blink-settings=imagesEnabled=false')
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
    p = 0
    r = []
    while 1:
        url = f'https://www.yelp.com/search?find_desc={main_key}&find_loc={keys}&ns=1&start={p * 10}'
        driver.get(url)
        print(url)
        driver.implicitly_wait(60)
        time.sleep(5)
        href_list = driver.find_elements_by_class_name('css-166la90')
        if not href_list:
            wirte_infos(r)
            break
        p += 1
        url_list = []
        print(r)
        for i in href_list:
            url_list.append(i.get_attribute('href'))
        for child_url in url_list:
            if not 'search' in child_url:
                find_data = SQLsession.query(Infos).filter_by(category=child_url).first()
                if not find_data:
                    driver.get(child_url)
                    try:
                        name = driver.find_element_by_class_name('css-11q1g5y').text
                    except:
                        name = ''
                    address, website, phone = '', '', ''
                    try:
                        info = driver.find_elements_by_class_name("border--left__373c0__1nKig")
                        target = ''
                        for ij in info:
                            try:
                                ij.find_element_by_class_name('css-1h1j0y3')
                                target = ij
                                break
                            except:
                                pass
                        ii = target.find_elements_by_class_name('css-1vhakgw')
                        for j in ii:
                            v = j.text
                            if '.' in v:
                                website = v
                            elif '(' in v:
                                phone = v.replace('Phone', '').replace('number', '').strip()
                            else:
                                address = v.replace('Get', '').replace('Directions', '').strip()
                        if not address:
                            try:
                                address = driver.find_element_by_tag_name("address").text
                            except:
                                pass
                    except Exception as e:
                        traceback.print_exc()
                    r.append(dict(name=name, website=website, phone=phone, address=address, groups='Yelp',
                                  source=keys + ' ' + main_key,
                                  category=child_url))
                    time.sleep(5)


if __name__ == '__main__':
    keys_list = read_txt()
    driver = get_driver()
    main_keys = ['wig install', 'sewin closure', 'hair bundle', 'Wigs Hair']
    breaklocation = ''
    for m in main_keys:
        for k in keys_list:
            if breaklocation == k or not breaklocation:
                get_data(driver, k, m)
                breaklocation = ''
                print(m + '___' + k)
