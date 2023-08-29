import random
import threading
from airtest.core.android.adb import ADB
from models import *
import time
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtest.core.android import Android


# 读取搜索标签
def read_txt():
    f = open('instagram.txt', 'r')
    text = f.read().split('\n')
    f.close()
    return text


def get_data(serialno, keys):
    datalist = []
    time.sleep(3)
    device = Android(serialno)
    poco = AndroidUiautomationPoco(device)
    device.unlock()
    device.unlock()
    device.wake()
    device.home()
    device.stop_app("com.instagram.android")
    device.start_app("com.instagram.android")
    # 点击搜索
    poco(name='Search and Explore').click()
    time.sleep(1)
    # 点击输入框
    poco(resourceId='com.instagram.android:id/action_bar_search_edit_text').click()
    # #输入框输入文字
    poco(name='com.instagram.android:id/action_bar_search_edit_text').set_text((keys))
    time.sleep(2)
    # child：第1个Top、第2个Accounts、第4个Tags、第5个Places，并点击
    container = poco(resourceId='com.instagram.android:id/tab_button_name_text')
    for i in container:
        if str(i.get_text()).lower() == 'tags':
            i.click()
            break
    time.sleep(3)
    # child：搜索结果下方第n行，并点击
    a = poco(resourceId='com.instagram.android:id/recycler_view')
    a[0].child()[0].click()
    poco(name='Recent').wait_for_appearance(120)
    poco(name='Recent').click()
    # 帖子
    try:
        poco(name='com.instagram.android:id/image_button')[0].click()
        time.sleep(2)
    except:
        poco.swipe([0.5, 0.2], [0.5, 0.8])
        time.sleep(10)
        poco(name='com.instagram.android:id/image_button')[0].click()
        time.sleep(2)
    # 获取用户名
    namelist = []
    # 滑屏
    for i in range(slide_num):
        try:
            time.sleep(1)
            name = poco(resourceId='com.instagram.android:id/row_feed_photo_profile_name').get_text().replace("•",
                                                                                                              "").strip()
            if name not in namelist:
                namelist.append(name)
            poco.swipe([0.5, 0.7], [0.5, 0.3], duration=random.uniform(0.8, 1))
        except:
            poco.swipe([0.5, 0.7], [0.5, 0.3], duration=random.uniform(0.8, 1))

    # 打开用户主页
    for name in list(set(namelist)):
        cmd = f'am start -a android.intent.action.VIEW -d instagram://user?username={name}'
        device.shell(cmd)
        time.sleep(3)
        try:
            # link
            website = poco(resourceId='com.instagram.android:id/profile_header_website').get_text()
        except:
            website = ""
        try:
            # category
            category = poco(resourceId='com.instagram.android:id/profile_header_business_category').get_text()
        except:
            category = ""
        try:
            # bio
            userbio = poco(resourceId='com.instagram.android:id/profile_header_bio_text')
            userbio.focus([0.999, 0.999]).click()
            time.sleep(1)
            bio = userbio.get_text()
        except:
            bio = ""
        phone, email = '', ''
        try:
            # Contact\Email
            if poco(text='Contact').exists():
                contact = poco(text='Contact')
                contact.click()
                time.sleep(1)
                options_rv = poco(resourceId='com.instagram.android:id/contact_options_rv').child()
                for i in options_rv:
                    if i.child()[0].get_text().lower() == 'text' or i.child()[0].get_text().lower() == 'call':
                        phone = i.child()[1].get_text()
                    if i.child()[0].get_text().lower() == 'email':
                        email = i.child()[1].get_text()
                for n in range(1):
                    device.keyevent('KEYCODE_BACK')

            elif poco(text='Call').exists():
                poco(text='Call').click()
                time.sleep(2)
                phone = poco(resourceId='com.google.android.dialer:id/digits').get_text()
                for n in range(3):
                    device.keyevent('KEYCODE_BACK')
            elif poco(text='Text').exists():
                poco(text='Text').click()
                time.sleep(2)
                phone = poco(resourceId='com.google.android.apps.messaging:id/conversation_title').get_text()
                for n in range(3):
                    device.keyevent('KEYCODE_BACK')
            elif poco(text='Email').exists():
                poco(text='Email').click()
                time.sleep(2)
                email = poco(resourceId='com.google.android.gm:id/peoplekit_chip').get_text()
                for n in range(3):
                    device.keyevent('KEYCODE_BACK')
        except:
            pass
        if bio or website or phone or email:
            find_data = SQLsession.query(Infos).filter_by(name=name).first()
            if not find_data:
                datalist.append(
                    dict(name=name, bio=bio, website=website, category=category, phone=phone, email=email,
                         groups='instagram', source=keys))
    print(datalist)

    for l in datalist:
        SQLsession.add(Infos(**l))
    SQLsession.commit()


def run_tag_list(serialno, tag_list):
    for keys in tag_list:
        print(keys)
        get_data(serialno, keys)


def main():
    """
    多线程执行多用户任务
    :return:
    """
    adbs = [d[0] for d in ADB().devices(state="device")]
    all_task = []
    tag_list = random.sample(read_txt(), len(adbs) * number)
    print(tag_list)
    for index, serialno in enumerate(adbs):
        # 使用多线程执行发帖任务
        t = threading.Thread(target=run_tag_list, args=(serialno, tag_list[index * number: (index + 1) * number]))
        t.setDaemon(True)
        t.start()
        all_task.append(t)
    # 等待线程执行结果
    for t in all_task:
        t.join()  # 设置主线程等待子线程结束
        print("in main: get page success")


if __name__ == '__main__':
    # 滑动次数
    slide_num = 300
    # 每台手机搜索标签数
    number = 2
    main()
