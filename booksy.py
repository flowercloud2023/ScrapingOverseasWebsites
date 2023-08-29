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
    p = 1
    # while循环，当执行到if not 时终止循环。
    while 1:
        # url_list为店铺的链接
        url_list = []
        # datalist存储每个店铺的name,phone,address
        datalist = []
        # 打开booksy
        url = f'https://booksy.com/en-us/s/{keys}?businessesPage={p}&query={main_key}'
        driver.get(url)
        print(main_key, keys, p)
        p += 1
        driver.implicitly_wait(60)
        time.sleep(5)
        # 父级标签一整页,a标签是商店链接，循环遍历整页的标签，输出链接aa，一页的写入列表url_list，换页再写入
        href = driver.find_element_by_class_name('purify_1C2sKfypqmjHLVLbn9OVsW').find_elements_by_css_selector(
            ".purify_T9Yll5MNBn5Dl2AemsAPX > a")
        for j in href:
            url_list.append(j.get_attribute('href'))
        # 如果链接不存在则break
        if not href:
            break
        # 遍历获取到的链接，一个个点进去获取信息
        for website in url_list:
            find_data = SQLsession.query(Infos).filter_by(website=website).first()
            if not find_data:
                driver.get(website)
                driver.implicitly_wait(60)
                time.sleep(5)
                try:
                    phone = driver.find_element_by_class_name("purify_spKYh8ojgB4tJ8IFc7ltQ").text
                except:
                    phone = ""
                # name和address同一个父级
                ad = driver.find_element_by_css_selector(
                    "[class='purify_L83AzFuVDcsMUGu-iworl purify_2se5gmL9KHmm2yN4OtqL_X purify_2SvKv3MmhxAqq-wQiZJQc3 purify_g4ZFx3Vp_j_IFmMZMFN6T']")
                try:
                    name = ad.find_element_by_css_selector(
                        "[class='purify_1sQI6P3rgyGZvU5pf3yAvt purify_3k1NnTEGO6TSunXbY5Zrkx']").text
                except:
                    name = ""
                try:
                    address = ad.find_element_by_css_selector(
                        "[class='purify_2U3GPA6ftCkPxPR_0NKXCC purify_Y1prq6mbHtuK9nWzbTqF9 purify_jEiYoKzkRbjQsWvwUztCr']").text
                except:
                    address = ""
                # 写入字典
                datalist.append(dict(name=name, website=website, phone=phone, address=address, groups='booksy',
                                     source=keys + ' ' + main_key))
        # 遍历字典，写入数据库
        for d in datalist:
            find_data = SQLsession.query(Infos).filter_by(name=d['name'], groups='booksy').first()
            if not find_data:
                SQLsession.add(Infos(**d))
        SQLsession.commit()


if __name__ == '__main__':
    # 无需地方关键字
    main_key = ['wig install', 'sewin closure', 'hair bundle', 'Wigs & Hair Pieces']
    keys_list = ['barber-shop', 'hair-salon']
    driver = get_driver()
    breaklocation = ''
    for mk in main_key:
        for k in keys_list:
            if breaklocation == k or not breaklocation:
                get_data(driver, k, mk)
                breaklocation = ''
                print(mk + '___' + k)