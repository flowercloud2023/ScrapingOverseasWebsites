import time
from selenium import webdriver
from models import *



def wirte_infos(data):
    for d in data:
        find_data = SQLsession.query(Infos).filter_by(name=d['name'], groups='Google').first()
        if not find_data:
            SQLsession.add(Infos(**d))
    SQLsession.commit()


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1440,1080')
    options.add_argument('--disable-extensions')
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')  # run Chrome use root
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #options.add_argument(
        #'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"')
    driver = webdriver.Chrome(options=options)
    return driver


def get_data(driver, keys):
    url = f'https://www.google.com/search?tbs=lf:1,lf_ui:14&tbm=lcl&q={keys}&rflfq=1&num=10&sa=X&ved=2ahUKEwiO_vvrt4fxAhVuHKYKHYrICFIQjGp6BAgFEF8&biw=1589&bih=718#rlfi=hd:;si:;mv:[[40.8399757,-73.73389089999999],[40.6529879,-74.2391999]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:14'
    driver.get(url)
    time.sleep(5)
    driver.find_element_by_id('mKlEF').click()
    time.sleep(5)
    r = []
    while 1:
        try:
            d = driver.find_element_by_css_selector("[class='rlfl__tls rl_tls']").find_elements_by_class_name('VkpGBb')
        except:break
        for i in d:
            try:
                i.find_element_by_class_name('dbg0pd').click()
                time.sleep(3)
            except: continue
            try:
                n = driver.find_element_by_css_selector("[class='SPZz6b']").find_element_by_tag_name('h2')
                name = n.text
            except:
                name = ''
            try:
                a = driver.find_element_by_css_selector("[class='LrzXr']")
                address = a.text
            except:
                address = ''
            try:
                p = driver.find_element_by_css_selector("[class='LrzXr zdqRlf kno-fv']")
                phone = p.text
            except:
                phone = ''
            try:
                w = i.find_element_by_css_selector("[class='yYlJEf L48Cpd']")
                website = w.get_attribute('href')
            except:
                website = ''
            if name or address or phone:
                r.append(dict(name=name, website=website, phone=phone, address=address, groups='Google', source=keys))
        try:
            ne = driver.find_elements_by_class_name('d6cvqb')[-1].find_element_by_tag_name('a')
            ne.click()
            time.sleep(5)
        except:
            break
    wirte_infos(r)


if __name__ == '__main__':
    main_key = ['wig', 'sewin closure', 'hair bundle']
    keys_list = read_txt()
    driver = get_driver()
    breaklocation = ''
    for mk in main_key:
        for k in keys_list:
            if breaklocation == k or not breaklocation:
                key = mk + ' in ' + k
                get_data(driver, key)
                breaklocation = ''
                print(key)

