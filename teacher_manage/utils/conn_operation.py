# -*- coding:utf-8 -*-
# date: 2017-09-20 19:21
import os
import re
import sys
import time
import queue
import datetime
import threading
import requests
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_manage.settings")
sys.path.append(os.path.dirname(__file__))
application = get_wsgi_application()
from operation.models import Cookies, Apply, BonusDetail, BonusCategory, UserAccount
from utils.page_parser import LoginPage, ApplyListPage, ApplyPage

# conn = requests.session()
# requests.utils.add_dict_to_cookiejar(conn.cookies, cookies)
# baidu = 'http://www.baidu.com'
# conn.get(baidu)
"""FDYStuActionExam_Edit.aspx?Id=522190&StudentId=2015121127&ObjectId=2-2"""


def store_conn_cookies(conn):
    Cookies.objects.all().delete()
    for k, v in conn.cookies.items():
        new_cookie = Cookies()
        new_cookie.name = k
        new_cookie.value = v
        print('cookie', k, v)
        new_cookie.save()


def get_conn_cookies(conn):
    cookie_dict = {}
    all_cookies = Cookies.objects.all()
    for cookie in all_cookies:
        name = cookie.name
        value = cookie.value
        cookie_dict[name] = value
    requests.utils.add_dict_to_cookiejar(conn.cookies, cookie_dict)
    return conn


class CrawThread(threading.Thread):
    def __init__(self, conn, queue1):
        threading.Thread.__init__(self)
        self.queue1 = queue1
        self.conn = conn

    def run(self):
        start_url = "http://xsc.cuit.edu.cn/Sys/SystemForm/StudentJudge/FDYStuActionExam.aspx"
        header = {
            'Host': 'xsc.cuit.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://xsc.cuit.edu.cn/Sys/SystemForm/Navigation.aspx',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        res = self.conn.get(start_url, headers=header)
        apply_list_page = ApplyListPage(res.content)
        all_href = apply_list_page.get_all_apply_href()
        count = 0
        for href in all_href:
            data = {}
            for para in href.split('?')[1].split('&'):
                para_couple = para.split('=')
                if len(para_couple) == 1:
                    data[para_couple[0]] = ''
                if len(para_couple) == 2:
                    data[para_couple[0]] = para_couple[1]
            apply_id = ''
            stu_id = ''
            if 'Id' in data:
                apply_id = data['Id'].strip()
            if 'StudentId' in data:
                stu_id = data['StudentId'].strip()
            # if apply_id and stu_id:
            #     try:
            #         new_apply = Apply.objects.get(apply_id=apply_id, stu_id=stu_id)
            #         if not new_apply.is_examined:
            #             continue
            #     except Exception as e:
            #         print(e)
            self.queue1.put(href)
            count += 1
        next_page_form = apply_list_page.get_next_page_form()
        data = {
            '__VIEWSTATE': next_page_form['__VIEWSTATE'],
            '__VIEWSTATEGENERATOR': next_page_form['__VIEWSTATEGENERATOR'],
            '__VIEWSTATEENCRYPTED': '',
            'FDYStatus': '0',
            'ClassNo': '',
            'StudentId': '',
            'Name': '',
            'BtnSearch': '查 询'.encode('gbk'),
            'GridView1$ctl02$StrId': next_page_form['GridView1$ctl02$StrId']
        }
        res = self.conn.post(start_url, headers=header, data=data)
        apply_list_page = ApplyListPage(res.content)
        max_page_num = apply_list_page.get_max_page_num()
        all_href = apply_list_page.get_all_apply_href()
        for href in all_href:
            data = {}
            for para in href.split('?')[1].split('&'):
                para_couple = para.split('=')
                if len(para_couple) == 1:
                    data[para_couple[0]] = ''
                if len(para_couple) == 2:
                    data[para_couple[0]] = para_couple[1]
            self.queue1.put(href)
            count += 1
        for i in range(2, max_page_num + 1):
            next_page_form = apply_list_page.get_next_page_form()
            next_page_form['__EVENTARGUMENT'] = 'Page$%d' % i
            res = self.conn.post(start_url, data=next_page_form, headers=header)
            apply_list_page = ApplyListPage(res.content)
            all_href = apply_list_page.get_all_apply_href()

            for href in all_href:
                self.queue1.put(href)
                count += 1
            print("all_count", count)


class ApplyCrawThread(threading.Thread):
    def __init__(self, conn, queue1, image_queue):
        threading.Thread.__init__(self)
        self.queue1 = queue1
        self.conn = conn
        self.image_queue = image_queue

    def run(self):
        header = {
            'Host': 'xsc.cuit.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://xsc.cuit.edu.cn/Sys/SystemForm/StudentJudge/FDYStuActionExam.aspx',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        failed_count = 0
        users = UserAccount.objects.filter(is_now_use=True)
        if users.count() > 0:
            user = users[0]
        else:
            try:
                user = UserAccount.objects.all()[0]
            except Exception:
                user = UserAccount(username='', password='')
                user.save()
        while True:
            try:
                a_new_href = self.queue1.get(block=True, timeout=5)  # 接收消息
                print('success to get a href %s' % a_new_href)
                apply_id_query = re.search(r"\?Id=\d+", a_new_href).group()
                apply_id = re.search(r'\d+', apply_id_query).group()
                res = self.conn.get(a_new_href, headers=header)
                # print(res.text)
                apply_page = ApplyPage(res.content)
                stu_id = apply_page.get_stu_id()
                stu_name = apply_page.get_stu_name()
                stu_class = apply_page.get_stu_class()
                apply_type = apply_page.get_apply_type()
                apply_year = apply_page.get_apply_year()
                is_add_score = apply_page.get_is_add_score()
                activity = apply_page.get_apply_content()
                apply_image = apply_page.get_apply_image()
                apply_status = apply_page.get_judge_status()
                bonus = apply_page.get_apply_bonus()
                apply_score = apply_page.get_apply_score()
                judge_content = apply_page.get_judge_content()
                # apply_default_score = apply_page.get_apply_default_score()
                view_states = apply_page.get_inputs()

                try:
                    new_apply = Apply.objects.get(apply_id=apply_id)
                    # if not new_apply.is_examined:
                    #     continue
                except Exception as e:
                    new_apply = Apply(user=user)

                new_apply.apply_id = apply_id
                new_apply.apply_url = a_new_href
                new_apply.is_add_score = is_add_score
                new_apply.apply_year = apply_year
                new_apply.stu_id = stu_id
                new_apply.stu_name = stu_name
                new_apply.stu_class = stu_class
                new_apply.apply_type = apply_type
                new_apply.activity = activity
                new_apply.examine_status = apply_status
                new_apply.examine_content = judge_content
                if apply_image:
                    self.image_queue.put(apply_image)
                    print('success put a image url in image queue')
                    # http://xsc.cuit.edu.cn/Sys/DownLoad/StudentJudge/2017911163757be5b87fa0aa349fb896c899756c634b3.jpg
                    image_name = apply_image[apply_image.rfind('/') + 1:]
                    image_local_path = "apply_image/" + image_name
                    new_apply.image = image_local_path
                if apply_score:
                    new_apply.apply_score = apply_score
                if len(bonus) == 1:
                    new_apply.bonus_category_id = int(bonus[0])
                if len(bonus) == 2:
                    new_apply.bonus_category_id = int(bonus[0])
                    new_apply.bonus_id = int(bonus[1])

                if '__VIEWSTATE' in view_states:
                    new_apply.view_state = view_states['__VIEWSTATE']
                if '__VIEWSTATEGENERATOR' in view_states:
                    new_apply.view_state_gen = view_states['__VIEWSTATEGENERATOR']
                try:
                    new_apply.save()
                    print('success to commit a apply')
                except Exception as e:
                    print('apply save error:', e)

            except queue.Empty:
                print('apply queue is empty')
                failed_count += 1
                time.sleep(10)
            if failed_count >= 3:
                break


class StoreImage(threading.Thread):
    def __init__(self, conn, image_queue, parent_dir_path):
        threading.Thread.__init__(self)
        self.image_queue = image_queue
        self.conn = conn
        self.parent_dir = parent_dir_path

    def run(self):
        failed_count = 0
        while True:
            try:
                image_url = self.image_queue.get(block=True, timeout=40)  # 接收消息
                # parent_dir = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
                static_path = self.parent_dir + "\image\\apply_image\\"
                image_name = image_url[image_url.rfind('/') + 1:]
                image_local_path = static_path + image_name
                if not os.path.exists(image_local_path):
                    res = self.conn.get(image_url)
                    with open(image_local_path, 'wb') as fp:
                        fp.write(res.content)
                    print('success to store a image')
            except queue.Empty:
                print("image queue is empty")
                failed_count += 1
            if failed_count >= 3:
                break


def apply_operation(conn, new_apply, operation_type='pass'):
    apply_url = new_apply.apply_url

    header = {
        'Host': 'xsc.cuit.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': apply_url,
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    view_state = new_apply.view_state
    view_state_gen = new_apply.view_state_gen
    score = new_apply.apply_score
    apply_content = new_apply.activity
    examine_content = new_apply.examine_content
    if not examine_content:
        examine_content = "同意"
    date = str(datetime.date.today())

    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': view_state,
        '__VIEWSTATEGENERATOR': view_state_gen,
        '__VIEWSTATEENCRYPTED': '',
        'ObjectInfo1$ActionThing': apply_content.encode('gbk'),
        'ObjectInfo1$Score': score,  # 新增（要改成的分数）
        'ObjectInfo1$FileImage': '',
        'FDYDate': date,
        'FDYThing': examine_content.encode('gbk'),
    }
    if operation_type == 'save':
        data['BtnSave'] = '保  存'.encode("gbk")
    elif operation_type == 'refuse':
        data['BtnSPDH'] = '审批打回'.encode('gbk')
    else:
        data['BtnSPTG'] = '审批通过'.encode('gbk')

    if new_apply.bonus:
        bonus_id = new_apply.bonus_id
        category_id = new_apply.bonus_category_id
        new_bonus = str(category_id) + "-" + str(bonus_id)

        try:
            bonus_detail = BonusDetail.objects.get(id=bonus_id)
            is_changeable = bonus_detail.is_changeable
            if is_changeable:
                # data['ObjectInfo1$Score'] = new_apply.apply_score
                max_credit = bonus_detail.max_score
                min_credit = bonus_detail.min_score
            else:
                new_apply.apply_score = max_credit = min_credit = bonus_detail.score
        except Exception as e:
            print('can\'t get the bonus detail id:', e)
            is_changeable = False
            max_credit = min_credit = new_apply.apply_score
        data['ObjectInfo1$ObjectList'] = new_bonus
        data['ObjectInfo1$smallcredit'] = min_credit
        data['ObjectInfo1$bigcredit'] = max_credit
    else:
        category_id = new_apply.bonus_category_id
        try:
            bonus_category = BonusCategory.objects.get(id=category_id)
            is_changeable = bonus_category.is_changeable
            if is_changeable:
                # data['ObjectInfo1$Score'] = new_apply.apply_score
                max_credit = bonus_category.max_score
                min_credit = bonus_category.min_score
            else:
                new_apply.apply_score = max_credit = min_credit = bonus_category.score
        except Exception as e:
            print('can\'t get the bonus_category id:', e)
            is_changeable = False
            max_credit = min_credit = new_apply.apply_score

        data['ObjectInfo1$smallcredit'] = min_credit
        data['ObjectInfo1$bigcredit'] = max_credit

    res = conn.post(apply_url, headers=header, data=data)
    new_apply_page = ApplyPage(res.content)
    alert_status = new_apply_page.get_alert_status()

    view_states = new_apply_page.get_inputs()
    print("alert_status is", alert_status)
    if '__VIEWSTATE' in view_states:
        new_apply.view_state = view_states['__VIEWSTATE']
    if '__VIEWSTATEGENERATOR' in view_states:
        new_apply.view_state_gen = view_states['__VIEWSTATEGENERATOR']
    new_apply.save()
    if operation_type == 'save':
        alert_status = apply_operation(conn, new_apply)
    else:
        try:
            apply_type = new_apply_page.get_apply_type()
        except AttributeError:
            return '账户已下线，请重新登录'
        is_add_score = new_apply_page.get_is_add_score()
        apply_status = new_apply_page.get_judge_status()
        bonus = new_apply_page.get_apply_bonus()
        apply_score = new_apply_page.get_apply_score()
        # apply_default_score = apply_page.get_apply_default_score()
        view_states = new_apply_page.get_inputs()
        judge_content = new_apply_page.get_judge_content()

        new_apply.is_add_score = is_add_score
        new_apply.apply_type = apply_type
        new_apply.examine_status = apply_status
        new_apply.examine_content = judge_content

        if apply_score:
            new_apply.apply_score = apply_score
        if len(bonus) == 1:
            new_apply.bonus_category_id = int(bonus[0])
        if len(bonus) == 2:
            new_apply.bonus_category_id = int(bonus[0])
            new_apply.bonus_id = int(bonus[1])

        if '__VIEWSTATE' in view_states:
            new_apply.view_state = view_states['__VIEWSTATE']
        if '__VIEWSTATEGENERATOR' in view_states:
            new_apply.view_state_gen = view_states['__VIEWSTATEGENERATOR']
        new_apply.is_examined = True  # 表示操作过了
        try:
            new_apply.save()
        except Exception as e:
            print('apply save error:', e)

    return alert_status


def download_new_data():
    conn = requests.session()
    conn = get_conn_cookies(conn)
    queue1 = queue.Queue()
    image_queue = queue.Queue()

    crawl_apply_list = CrawThread(conn, queue1)

    apply_craw1 = ApplyCrawThread(conn, queue1, image_queue)
    apply_craw2 = ApplyCrawThread(conn, queue1, image_queue)

    # parent_dir = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
    # image_crawl1 = StoreImage(conn, image_queue, parent_dir)
    # image_crawl2 = StoreImage(conn, image_queue, parent_dir)

    crawl_apply_list.start()
    apply_craw1.start()
    apply_craw2.start()
    # image_crawl1.start()
    # image_crawl2.start()
    store_conn_cookies(conn)


# if __name__ == '__main__':
    # conn = requests.session()
    # # conn = get_conn_cookies(conn)
    # cookie = {
    #     'ASP.NET_SessionId': '5td2xblwniuu11qgj5jqeyab',
    #     'UM_distinctid': '165c3f67021486-092fe8f886e06f-78704126-1fa400-165c3f670224d0',
    #     'CNZZDATA1000271341': '1265773513-1536589044-http%253A%252F%252Fxsc.cuit.edu.cn%252F%7C1537888128',
    #     'CenterSoft': '1693E31946E811DF89BFABE288585DAD36A1C28A15774B83692C356BF212EB39BD79C64071BE73136A08309669B9785F682E1C6D774E8147200BDC041253239A06099224E78B718528F75E5566688541AD86BB3CBB2DD260BDDFD31B579B5E7EE6E1E9BA62FF2D0B3CF13C44BB937939BF3825586D375F1039DE7192C489F9F8083E925702F2615C0536F6975A3D3C965CDE07C86A417EEB9D194A34F7CF1E6250DC20DA192637D1A0B4FC41'
    # }
    # requests.utils.add_dict_to_cookiejar(conn.cookies, cookie)
    # start_url = "http://xsc.cuit.edu.cn/Sys/SystemForm/StudentJudge/FDYStuActionExam.aspx"
    # header = {
    #     'Host': 'xsc.cuit.edu.cn',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #     'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    #     'Accept-Encoding': 'gzip, deflate',
    #     'Referer': 'http://xsc.cuit.edu.cn/Sys/SystemForm/Navigation.aspx',
    #     'Connection': 'keep-alive',
    # }
    # res = conn.get(start_url, headers=header)
    # apply_list_page = ApplyListPage(res.content)
    # # max_page_num = apply_list_page.get_max_page_num()
    # all_href = apply_list_page.get_all_apply_href()
    # count = 0
    # print(all_href)
    # next_page_form = apply_list_page.get_next_page_form()
    # data = {
    #     '__VIEWSTATE': next_page_form['__VIEWSTATE'],
    #     '__VIEWSTATEGENERATOR': next_page_form['__VIEWSTATEGENERATOR'],
    #     '__VIEWSTATEENCRYPTED': '',
    #     'FDYStatus': '0',
    #     'ClassNo': '',
    #     'StudentId': '',
    #     'Name': '',
    #     'BtnSearch': '查 询'.encode('gbk'),
    #     'GridView1$ctl02$StrId': next_page_form['GridView1$ctl02$StrId']
    # }
    # print(data)
    # res = conn.post(start_url, headers=header,data=data)
    # apply_list_page = ApplyListPage(res.content)
    # max_page_num = apply_list_page.get_max_page_num()
    # print(all_href, max_page_num)
    # for i in range(2, max_page_num + 1):
    #     next_page_form = apply_list_page.get_next_page_form()
    #     next_page_form['__EVENTARGUMENT'] = 'Page$%d' % i
    #     res = conn.post(start_url, data=next_page_form, headers=header)
    #     apply_list_page = ApplyListPage(res.content)
    #     all_href = apply_list_page.get_all_apply_href()
    #     print(all_href)
    # stu_apply = Apply.objects.filter(apply_id=648296)
    # for apply in stu_apply:
    #     apply.bonus_id = 21
    #     status = apply_operation(conn, apply, 'save')
    #     print(status)
# http://xsc.cuit.edu.cn/Sys/SystemForm/StudentJudge/FDYStuActionExam_Edit.aspx?Id=550722&StudentId=2015082042&ObjectId=1
# http://xsc.cuit.edu.cn/Sys/SystemForm/StudentJudge/FDYStuActionExam_Edit.aspx?Id=522190&StudentId=2015121127&ObjectId=2-2
# http://xsc.cuit.edu.cn/Sys/SystemForm/FDYStuActionExam_Edit.aspx?Id=550722&StudentId=2015082042&ObjectId=1
