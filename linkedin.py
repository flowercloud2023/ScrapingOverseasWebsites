import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from models import *
from pywinauto.application import Application
import win32clipboard as w

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def setText(aString):  # 写入剪切板
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardText(aString)
    w.CloseClipboard()


def run_Chrome():
    app = Application().start(r'c:\WINDOWS\System32\cmd.exe /k', create_new_console=True, wait_for_idle=False)
    window = app.top_window()
    window.type_keys("\r", with_spaces=True)
    window.type_keys("c:\r", with_spaces=True)
    setText(r"cd C:\\Program Files\\Google\\Chrome\\Application")
    window.type_keys('^v\r')
    window.type_keys("chrome.exe --remote-debugging-port=9999\r", with_spaces=True)
    return window


def get_user_browser(username, password):
    options = Options()
    # 修改chrome设置
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9999")
    driver = webdriver.Chrome(options=options)
    # driver.get('https://www.baidu.com/')
    driver.get(login_url)
    driver.implicitly_wait(page_delay)
    # driver.find_element_by_name('session_key').send_keys(username)
    # time.sleep(3)
    # driver.find_element_by_name('session_password').send_keys(password)
    # time.sleep(5)
    # driver.find_element_by_name('login-submit').click()
    # time.sleep(1)
    driver.implicitly_wait(page_delay)
    time.sleep(2)
    cookiesList = driver.get_cookies()
    cookiesDict = {}
    for i in cookiesList:
        cookiesDict[i['name']] = i['value']
    return cookiesDict, driver


def main(source):
    # 查找所有账户
    window = run_Chrome()
    link_list = []
    p = 1
    cookiesDict, driver = get_user_browser(username, password)
    time.sleep(1)
    # driver.find_element_by_css_selector("[class='search-global-typeahead__input always-show-placeholder']").send_keys("salon hair")
    # time.sleep(2)
    # ActionChains(driver).send_keys(Keys.ENTER).perform()
    # time.sleep(2)

    while 1:
        url = f'https://www.linkedin.com/search/results/companies/?keywords={source}&origin=SWITCH_SEARCH_VERTICAL&page={p}'
        driver.get(url)
        print("page:", p, "url:", url)
        time.sleep(2)
        p += 1
        ss = []
        # ss = driver.find_element_by_css_selector("[class='display-flex overflow-hidden ']")find_elements_by_css_selector("[class='search-reusables__primary-filter']")[3].click()
        # link = driver.find_element_by_css_selector("[class='reusable-search__entity-results-list list-style-none']")
        aa = driver.find_elements_by_css_selector("[class='app-aware-link']")
        print(len(aa))
        if len(aa) == 0:
            break
        # time.sleep(1)
        for i in aa:
            d = i.get_attribute("href")
            print(d)
            link_list.append(d)
            print(link_list)
            # set方法是对元素进行去重，处理之后是一个字典形式，使用list是将其转化为列表。
        link_list = list(set(link_list))
        time.sleep(1)

        for s in link_list:
            driver.get(s + 'about/')
            name = driver.find_element_by_css_selector("h1").text
            print(name)
            # time.sleep(1)
            camkey = driver.find_elements_by_css_selector(
                "[class='org-page-details__definition-term t-14 t-black t-bold']")
            camvalue = driver.find_elements_by_css_selector(
                "[class='org-page-details__definition-text t-14 t-black--light t-normal']")
            d = {'name': name}
            for k in camkey:
                if k.text == 'Company size':
                    camkey.remove(k)

            for k, v in zip(camkey, camvalue):
                # print("key: ",k.text," , value: ",v.text)
                if k.text == 'Website':
                    d['website'] = v.text
                if k.text == 'Phone':
                    d['phone'] = v.find_element_by_tag_name('span').text
                if k.text == 'Industry':
                    d['category'] = v.text
                if k.text == 'Headquarters':
                    d['address'] = v.text
                if k.text == 'Specialties':
                    d['bio'] = v.text
            time.sleep(1)
            # print(d)
            ss.append(dict(d, groups='linkedin', source=source))
            print(ss)

        # 遍历写入数据库
        for z in ss:
            find_data = SQLsession.query(Infos).filter_by(name=z['name']).first()
            if not find_data:
                SQLsession.add(Infos(**z))
        SQLsession.commit()
        time.sleep(1)

    driver.close()
    window.close()


if __name__ == '__main__':
    page_delay = 20
    login_url = 'https://www.linkedin.com/feed/?trk=guest_homepage-basic_nav-header-signin'
    # login_url = 'https://www.linkedin.com/login/zh-cn?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    sourcelist = ["salon hair", "wigs"]
    for source in sourcelist:
        print(source)
        main(source)
