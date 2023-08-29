import time
from selenium import webdriver
from models import *


def wirte_infos(data):
    for d in data:
        SQLsession.add(Comments(**d))
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

def get_data(driver, keys):
    p = 0
    r = []
    global start
    if start:
        p = p + start
        start = 0
    while 1:
        url = f'https://www.yelp.com/search?find_desc=African%20American%20Hair%20Salons&find_loc={keys}&ns=1&start={p * 10}'
        driver.get(url)
        print(url)
        driver.implicitly_wait(60)
        time.sleep(10)
        href_list = driver.find_elements_by_class_name('css-166la90')
        if not href_list:
            break
        p += 1
        url_list = []
        print(r)
        for i in href_list:
            url_list.append(i.get_attribute('href'))
        for child_url in url_list:
            if not 'search' in child_url:
                index = 0
                source = ''
                while 1:
                    cu = child_url + '&start=' + str(index * 10)
                    driver.get(cu)
                    if index == 0:
                        source = driver.find_element_by_class_name('css-11q1g5y').text
                        if SQLsession.query(Comments).filter_by(source=source).first():
                            break
                    get_infos = driver.find_elements_by_css_selector(' .review__373c0__13kpL.border-color--default__373c0__2oFDT')
                    print(len(get_infos))
                    for j in get_infos:
                        score = j.find_element_by_class_name('overflow--hidden__373c0__2B0kz').get_attribute('aria-label').replace('star rating', '').strip()
                        comment_date = j.find_element_by_css_selector(' .css-e81eai').text
                        content = j.find_element_by_css_selector('.comment__373c0__1M-px.css-n6i4z7').text
                        r.append(dict(score=score, comment_date=comment_date, content=content, source=source))
                    if not get_infos:
                        wirte_infos(r)
                        r = []
                        break
                    time.sleep(5)
                    index += 1

if __name__ == '__main__':
    start = 15
    keys_list = ['TX', 'IL', 'GA']
    driver = get_driver()
    for k in keys_list:
        get_data(driver, k)
