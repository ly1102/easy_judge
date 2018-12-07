import os
import io
import json
import math
import time
import xlwt
import queue
import requests
import datetime
import xlsxwriter
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from operation.models import Apply, BonusCategory, BonusDetail, Cookies, UserAccount
from utils.conn_operation import store_conn_cookies, get_conn_cookies, CrawThread, ApplyCrawThread, StoreImage, \
    apply_operation
from utils.page_parser import LoginPage
from web_manage.settings import MEDIA_URL, STATIC_URL


# Create your views here.


# def json_response(func):
#     """
#     A decorator thats takes a view response and turns it
#     into json. If a callback is added through GET or POST
#     the response is JSONP.
#     """
#
#     def decorator(request, *args, **kwargs):
#         objects = func(request, *args, **kwargs)
#         if isinstance(objects, HttpResponse):
#             return objects
#         try:
#             data = json.dumps(objects)
#             if 'callback' in request.REQUEST:
#                 # a jsonp response!
#                 data = '%s(%s);' % (request.REQUEST['callback'], data)
#                 return HttpResponse(data, "text/javascript")
#         except:
#             data = json.dumps(str(objects))
#         response = HttpResponse(data, content_type="application/json")
#         response['Access-Control-Allow-Origin'] = '*'
#         return response
#
#     return decorator


class LoginView(View):
    def get(self, request):
        conn = requests.session()
        header = {
            'Host': 'xsc.cuit.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://xsc.cuit.edu.cn',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        login_url = "http://xsc.cuit.edu.cn/Sys/UserLogin.html"
        captcha_url = "http://xsc.cuit.edu.cn/Sys/default3.html"
        login_res = conn.get(login_url, headers=header)
        login_page = LoginPage(login_res.content)
        input_dict = login_page.get_all_hidden_input()

        view_state = ''
        view_state_generator = ''
        event_validation = ''

        if '__VIEWSTATE' in input_dict:
            view_state = input_dict['__VIEWSTATE']
        if '__VIEWSTATEGENERATOR' in input_dict:
            view_state_generator = input_dict['__VIEWSTATEGENERATOR']
        if '__EVENTVALIDATION' in input_dict:
            event_validation = input_dict['__EVENTVALIDATION']
        # print(view_state)
        # print(view_state_generator)
        # print(event_validation)
        captcha_res = conn.get(captcha_url)
        if captcha_res.status_code != 200:
            alert = '<script>alert("获取验证码失败！可能是网络不稳定或太多人使用网站。请刷新重试。")</script>'
        else:
            pd = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
            captcha_path = pd + STATIC_URL.replace("/", "\\") + "captcha.jpg"
            with open(captcha_path, 'wb') as fp:
                fp.write(captcha_res.content)
            alert = ''

        store_conn_cookies(conn)

        last_logins = UserAccount.objects.all().values('last_login')
        now = datetime.datetime.now()
        last_login = None
        for login in last_logins:
            login_time = login['last_login']
            if (now - login_time).days >= 60:
                if last_login is None:
                    last_login = login_time
                elif (last_login - login_time).days >= 1:
                    last_login = login_time
        if last_login is None:
            need_alert = False
        else:
            need_alert = True
            last_login = last_login.strftime('%Y-%m-%d %H:%M:%S')
        last_users = UserAccount.objects.filter(is_now_use=True)
        if last_users.count() > 0:
            last_user = last_users[0]
            username = last_user.username
            password = last_user.password
        else:
            username = password = ''
        return render(request, 'new_login.html', {
            'alert': alert,
            'view_state': view_state,
            'view_state_generator': view_state_generator,
            'event_validation': event_validation,
            'need_alert': need_alert,
            'last_login': last_login,
            'username': username,
            'password': password
        })

    def post(self, request):
        conn = requests.session()
        conn = get_conn_cookies(conn)

        user_name = request.POST.get("UserName", '')
        password = request.POST.get("UserPass", '')
        check_code = request.POST.get("CheckCode", "")
        view_state = request.POST.get('__VIEWSTATE', '')
        view_state_generator = request.POST.get('__VIEWSTATEGENERATOR', '')
        event_validation = request.POST.get('__EVENTVALIDATION', '')

        data = {
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_state_generator,
            '__EVENTVALIDATION': event_validation,
            'UserName': user_name,
            'UserPass': password,
            'CheckCode': check_code,
            'Btn_OK.x': '25',
            'Btn_OK.y': '26',
        }

        header = {
            'Host': 'xsc.cuit.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'ccept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://xsc.cuit.edu.cn/Sys/UserLogin.html',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        login_url = "http://xsc.cuit.edu.cn/Sys/UserLogin.html"
        login_res = conn.post(login_url, headers=header, data=data)
        login_page = LoginPage(login_res.content)
        alert = login_page.get_login_ok_alert()
        if alert:
            header = {
                'Host': 'xsc.cuit.edu.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'http://xsc.cuit.edu.cn',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
            login_url = "http://xsc.cuit.edu.cn/Sys/UserLogin.html"
            captcha_url = "http://xsc.cuit.edu.cn/Sys/default3.html"
            login_res = conn.get(login_url, headers=header)
            login_page = LoginPage(login_res.content)
            input_dict = login_page.get_all_hidden_input()

            view_state = ''
            view_state_generator = ''
            event_validation = ''

            if '__VIEWSTATE' in input_dict:
                view_state = input_dict['__VIEWSTATE']
            if '__VIEWSTATEGENERATOR' in input_dict:
                view_state_generator = input_dict['__VIEWSTATEGENERATOR']
            if '__EVENTVALIDATION' in input_dict:
                event_validation = input_dict['__EVENTVALIDATION']
            # print(view_state)
            # print(view_state_generator)
            # print(event_validation)
            captcha_res = conn.get(captcha_url)
            pd = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
            captcha_path = pd + STATIC_URL.replace("/", "\\") + "captcha.jpg"
            with open(captcha_path, 'wb') as fp:
                fp.write(captcha_res.content)
            print(alert)
            if '请注销用户' in str(alert):
                exit_url = "http://xsc.cuit.edu.cn/Sys/SystemForm/ExitWindows.aspx"
                # conn.get(exit_url)
                return HttpResponseRedirect("/init")

            store_conn_cookies(conn)

            last_logins = UserAccount.objects.all().values('last_login')
            now = datetime.datetime.now()
            last_login = None
            for login_time in last_logins:
                if (now - login_time).year >= 1:
                    if last_login is None:
                        last_login = login_time
                    elif (last_login - login_time).days >= 1:
                        last_login = login_time
            if last_login is None:
                need_alert = False
            else:
                need_alert = True
                last_login = last_login.strftime('%Y-%m-%d %H:%M:%S')
            last_users = UserAccount.objects.filter(is_now_use=True)
            if last_users.count() > 0:
                last_user = last_users[0]
                username = last_user.username
                password = last_user.password
            else:
                username = password = ''

            return render(request, 'new_login.html', {
                'alert': str(alert),
                'view_state': view_state,
                'view_state_generator': view_state_generator,
                'event_validation': event_validation,
                'need_alert': need_alert,
                'last_login': last_login,
                'username': username,
                'password': password
            })
        else:
            # conn = requests.session()
            # conn = get_conn_cookies(conn)
            # 检测用户是否登录过，用以判断新账户
            UserAccount.objects.all().update(is_now_use=False)
            try:
                user_account = UserAccount.objects.get(username=user_name)
                user_account.last_login = datetime.datetime.now()
                user_account.is_now_use = True
                user_account.save()
            except Exception:
                user_account = UserAccount(username=user_name, password=password, is_now_use=True)
                user_account.save()

            request.session['user_id'] = user_account.id

            queue1 = queue.Queue()
            image_queue = queue.Queue()

            crawl_apply_list = CrawThread(conn, queue1)

            apply_craw1 = ApplyCrawThread(conn, queue1, image_queue)
            apply_craw2 = ApplyCrawThread(conn, queue1, image_queue)

            parent_dir = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
            image_crawl1 = StoreImage(conn, image_queue, parent_dir)
            image_crawl2 = StoreImage(conn, image_queue, parent_dir)

            crawl_apply_list.start()
            apply_craw1.start()
            apply_craw2.start()
            image_crawl1.start()
            image_crawl2.start()
            store_conn_cookies(conn)
            time.sleep(2)
            return HttpResponseRedirect("/init?init=1")


class ApplyListView(View):
    def get(self, request):
        def get_apply(page_num, key, value, is_add_score, year, user, limit=20, is_examined_type=''):
            if is_examined_type == '':
                is_examined_type = '等待审批'
            if is_examined_type in ['审批通过', '审批打回', '等待审批']:
                examined_status = True
            else:
                examined_status = False

            if key == "stu_id":
                all_apply = Apply.objects.filter(stu_id=value, is_add_score=is_add_score, user=user).order_by("stu_id")
            elif key == "stu_name":
                all_apply = Apply.objects.filter(stu_name=value, is_add_score=is_add_score, user=user).order_by(
                    "stu_id")
            elif key == "stu_class":
                all_apply = Apply.objects.filter(stu_class=value, is_add_score=is_add_score, user=user).order_by(
                    "stu_id")
            else:
                all_apply = Apply.objects.all().order_by("stu_id")

            if examined_status:
                all_apply = all_apply.filter(examine_status=is_examined_type)

            # if examined_status != 'all':
            #     all_apply = all_apply.filter(is_examined=examined_status)

            if year:
                all_apply = all_apply.filter(apply_year=year)

            all_apply_count = all_apply.count()
            max_page_num = math.ceil(all_apply_count / limit)
            page_count = page_num * limit
            if page_count >= all_apply_count:
                if page_count - limit > all_apply_count:
                    page_reply = []  # 当页面要求数大于当前最大数量，返回空
                else:
                    page_reply = all_apply[page_count - limit:]
            else:
                page_reply = all_apply[page_count - limit: page_count]

            return page_reply, max_page_num

        def covert_reply_dict(page_reply, page_num, max_page_num):

            def get_apply_info(apply):
                category = {}
                stu_id = apply.stu_id
                stu_name = apply.stu_name
                stu_class = apply.stu_class
                apply_id = apply.apply_id
                apply_content = apply.activity
                apply_image = apply.image
                apply_score = apply.apply_score
                apply_type = apply.apply_type
                apply_status = apply.examine_status
                category['apply_id'] = apply_id
                category['stu_id'] = stu_id
                category['stu_name'] = stu_name
                category['stu_class'] = stu_class
                category['apply_content'] = apply_content
                category['apply_year'] = apply.apply_year
                category['judge_content'] = apply.examine_content
                if apply_image:
                    category['apply_image'] = MEDIA_URL + str(apply_image)
                else:
                    category['apply_image'] = None
                category['apply_score'] = apply_score
                category['apply_type'] = apply_type
                category['apply_status'] = apply_status

                bonus_category_id = apply.bonus_category_id
                all_bonus_category = BonusCategory.objects.filter(id=bonus_category_id)
                bonus_count = all_bonus_category.count()
                if bonus_count == 0:
                    return None
                else:
                    bonus_category = all_bonus_category[0]
                changeable = bonus_category.is_changeable
                bonus_category_name = bonus_category.content
                category['apply_category'] = bonus_category_name
                if changeable:
                    category['changeable'] = True
                    max_score = bonus_category.max_score
                    min_score = bonus_category.min_score
                    category['max_score'] = max_score
                    category['min_score'] = min_score
                else:
                    category['changeable'] = False

                all_bonus_detail_list = []
                bonus_detail_id = apply.bonus_id
                if bonus_detail_id:
                    all_bonus_detail = BonusDetail.objects.filter(bonus_category_id_id=bonus_category_id).order_by(
                        "score")
                    for bonus_detail in all_bonus_detail:
                        option = {}
                        option_name = bonus_detail.selection
                        option_id = bonus_detail.id
                        option_score = bonus_detail.score

                        if option_id == bonus_detail_id:
                            option['selected'] = True

                        changeable = bonus_detail.is_changeable
                        if changeable:
                            option['changeable'] = True
                            max_score = bonus_detail.max_score
                            min_score = bonus_detail.min_score
                            option['max_score'] = max_score
                            option['min_score'] = min_score
                        else:
                            option['changeable'] = False
                        option['option_name'] = option_name
                        option['option_id'] = option_id
                        option['option_score'] = option_score
                        all_bonus_detail_list.append(option)
                category['options'] = all_bonus_detail_list
                return category

            data = {
                "status": "success",
                "page_num": page_num,
                "max_page_num": max_page_num
            }
            replies_list = []
            for each_apply in page_reply:
                each_apply_dict = get_apply_info(each_apply)
                replies_list.append(each_apply_dict)
            data['data'] = replies_list
            return data

        page_num = request.GET.get("page", "")
        if not page_num:
            page_num = 1
        else:
            try:
                page_num = int(page_num)
            except Exception as e:
                page_num = 1
        judge_type = request.GET.get('type', '')
        stu_id = request.GET.get("stu_id", "")
        stu_name = request.GET.get("stu_name", "")
        stu_class = request.GET.get("stu_class", "")
        is_add_score = request.GET.get('is_add', "")
        year = request.GET.get('year', '')
        try:
            user = UserAccount.objects.get(id=request.session['user_id'])
        except Exception:
            users = UserAccount.objects.filter(is_now_use=True)
            if users.count() > 0:
                user = users[0]
            else:
                user = UserAccount.objects.all()[0]

        if is_add_score == "0":
            is_add_score = False
        else:
            is_add_score = True
        json_dict = {
            "status": "success",
        }
        if stu_class == '等待审批':
            stu_class = ''

        if stu_id:
            try:
                page_reply, max_page_num = get_apply(page_num, "stu_id", stu_id, is_add_score, year, user,
                                                     is_examined_type=judge_type)
                applies_list = covert_reply_dict(page_reply, page_num, max_page_num)
                json_dict['apply_info'] = applies_list
                return HttpResponse(json.dumps(json_dict), content_type='application/json')
            except Exception as e:
                print('send applies render error:', e)
                json_dict['status'] = 'fail'
                return HttpResponse(json.dumps(json_dict), content_type='application/json')

        if stu_name:
            try:
                page_reply, max_page_num = get_apply(page_num, "stu_name", stu_name, is_add_score, year, user,
                                                     is_examined_type=judge_type)
                applies_list = covert_reply_dict(page_reply, page_num, max_page_num)
                json_dict['apply_info'] = applies_list
                return HttpResponse(json.dumps(json_dict), content_type='application/json')
            except Exception as e:
                print('send applies render error:', e)
                json_dict['status'] = 'fail'
                return HttpResponse(json.dumps(json_dict), content_type='application/json')

        if stu_class:
            try:
                page_reply, max_page_num = get_apply(page_num, "stu_class", stu_class, is_add_score, year, user,
                                                     is_examined_type=judge_type)
                applies_list = covert_reply_dict(page_reply, page_num, max_page_num)
                json_dict['apply_info'] = applies_list
                return HttpResponse(json.dumps(json_dict), content_type='application/json')
            except Exception as e:
                print('send applies render error:', e)
                json_dict['status'] = 'fail'
                return HttpResponse(json.dumps(json_dict), content_type='application/json')

        try:
            page_reply, max_page_num = get_apply(page_num, "all_reply", "no_filter", is_add_score, year, user,
                                                 is_examined_type=judge_type)
            applies_list = covert_reply_dict(page_reply, page_num, max_page_num)
            json_dict['apply_info'] = applies_list
            return HttpResponse(json.dumps(json_dict), content_type='application/json')
        except Exception as e:
            print('send applies render error:', e)
            json_dict['status'] = 'fail'
            return HttpResponse(json.dumps(json_dict), content_type='application/json')
            # return json_dict


class ApplyInitView(View):
    def get(self, request):
        is_init = request.GET.get('init', '')
        if is_init:
            is_init = 'true'
        else:
            is_init = 'false'
        return render(request, 'index.html', {'is_init': is_init})


class UserOperation(View):
    def post(self, request):
        post_apply_id = request.POST.get("apply_id", "")
        post_stu_id = request.POST.get("stu_id", "")
        post_option_id = request.POST.get("option_id", "")
        post_apply_score = request.POST.get("apply_score", "")
        examine_content = request.POST.get("examine_content", "")
        examine_type = request.POST.get("examine_type", "")

        if not (post_apply_id and post_stu_id and post_apply_score):
            data = {
                "status": "fail",
                "msg": "未接收到申请id或学号或分数",
            }
            return HttpResponse(json.dumps(data), content_type='application/json')
        apply_query_sets = Apply.objects.filter(apply_id=post_apply_id, stu_id=post_stu_id)
        print(len(apply_query_sets))
        if not apply_query_sets:
            data = {
                "status": "fail",
                "msg": "没有查找到对应申请",
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

        conn = requests.session()
        conn = get_conn_cookies(conn)

        for stu_apply in apply_query_sets:
            # 首先获取申请信息。。。
            stu_apply.examine_content = examine_content

            if examine_type == "refuse":
                # 打回的函数****
                status = apply_operation(conn, stu_apply, operation_type='refuse')
                if status == True or status == '':
                    data = {
                        "status": "success",
                        "msg": "打回成功",
                    }
                else:
                    data = {
                        "status": "fail",
                        "msg": status,
                    }
                return HttpResponse(json.dumps(data), content_type='application/json')

            if stu_apply.apply_score != float(post_apply_score):
                if post_option_id and stu_apply.bonus:
                    bonus_id = stu_apply.bonus_id
                    if post_option_id.isalnum() and post_option_id != bonus_id:
                        stu_apply.bonus_id = int(post_option_id)

                stu_apply.apply_score = post_apply_score
                stu_apply.save()

                # 提交修改请求，并通过****
                status = apply_operation(conn, stu_apply, operation_type='save')
                if status == True:
                    data = {
                        "status": "success",
                        "msg": "成功保存并提交",
                    }
                else:
                    data = {
                        "status": "fail",
                        "msg": status,
                    }
                return HttpResponse(json.dumps(data), content_type='application/json')

            # 直接审核通过****
            status = apply_operation(conn, stu_apply, operation_type='pass')
            if status == True:
                data = {
                    "status": "success",
                    "msg": "成功提交",
                }
            else:
                data = {
                    "status": "fail",
                    "msg": status,
                }
            return HttpResponse(json.dumps(data), content_type='application/json')

        # 出错提示
        data = {
            "status": "fail",
            "msg": "没有查找到对应申请",
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


class ClassView(View):
    def get(self, request):
        all_class = Apply.objects.values('stu_class')
        all_class_name = list(set([i['stu_class'] for i in all_class]))
        all_class_name.sort()
        return HttpResponse(json.dumps({'classes': all_class_name}))


class YearView(View):
    def get(self, request):
        all_class = Apply.objects.values('apply_year')
        all_class_name = list(set([i['apply_year'] for i in all_class]))
        all_class_name.sort()
        return HttpResponse(json.dumps({'years': all_class_name}))


class ClearDataView(View):
    def get(self, request):
        try:
            Apply.objects.all().delete()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': True, 'msg': str(e)})


class ExitLoginView(View):
    def get(self, request):
        try:
            Cookies.objects.all().delete()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': True, 'msg': str(e)})


class GetNewDataView(View):

    def get(self, request):
        conn = requests.session()
        conn = get_conn_cookies(conn)
        queue1 = queue.Queue()
        image_queue = queue.Queue()

        crawl_apply_list = CrawThread(conn, queue1)

        apply_craw1 = ApplyCrawThread(conn, queue1, image_queue)
        apply_craw2 = ApplyCrawThread(conn, queue1, image_queue)

        parent_dir = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
        image_crawl1 = StoreImage(conn, image_queue, parent_dir)
        image_crawl2 = StoreImage(conn, image_queue, parent_dir)

        crawl_apply_list.start()
        apply_craw1.start()
        apply_craw2.start()
        image_crawl1.start()
        image_crawl2.start()
        store_conn_cookies(conn)
        while True:
            try:
                if not crawl_apply_list.is_alive() and not apply_craw1.is_alive() and not image_crawl1.is_alive():
                    return JsonResponse({'status': True})
            except Exception as e:
                return JsonResponse({'status': True, 'msg': str(e)})


class ExportView(View):
    def get(self, request):
        def get_apply(key, value, is_add_score, year, user, is_examined_type=''):
            if is_examined_type in ['审批通过', '审批打回', '等待审批']:
                examined_status = True
            else:
                examined_status = False

            if key == "stu_id":
                all_apply = Apply.objects.filter(stu_id=value, is_add_score=is_add_score, user=user).order_by("stu_id")
            elif key == "stu_name":
                all_apply = Apply.objects.filter(stu_name=value, is_add_score=is_add_score, user=user).order_by(
                    "stu_id")
            elif key == "stu_class":
                all_apply = Apply.objects.filter(stu_class=value, is_add_score=is_add_score, user=user).order_by(
                    "stu_id")
            else:
                all_apply = Apply.objects.all().order_by("stu_id")

            if examined_status:
                all_apply = all_apply.filter(examine_status=is_examined_type)

            # if examined_status != 'all':
            #     all_apply = all_apply.filter(is_examined=examined_status)

            if year:
                all_apply = all_apply.filter(apply_year=year)

            return all_apply

        export_type = request.GET.get('export_type', '')
        judge_type = request.GET.get('type', '')
        stu_id = request.GET.get("stu_id", "")
        stu_name = request.GET.get("stu_name", "")
        stu_class = request.GET.get("stu_class", "")
        is_add_score = request.GET.get('is_add', "")
        year = request.GET.get('year', '')
        try:
            user = UserAccount.objects.get(id=request.session['user_id'])
        except Exception:
            users = UserAccount.objects.filter(is_now_use=True)
            if users.count() > 0:
                user = users[0]
            else:
                user = UserAccount.objects.all()[0]

        if is_add_score == "0":
            is_add_score = False
        else:
            is_add_score = True

        if stu_class == '等待审批':
            stu_class = ''

        if stu_id:
            page_reply, = get_apply("stu_id", stu_id, is_add_score, year, user,
                                    is_examined_type=judge_type)

        elif stu_name:
            page_reply = get_apply("stu_name", stu_name, is_add_score, year, user,
                                   is_examined_type=judge_type)

        elif stu_class:
            page_reply = get_apply("stu_class", stu_class, is_add_score, year, user,
                                   is_examined_type=judge_type)
        else:
            page_reply = get_apply("all_reply", "no_filter", is_add_score, year, user,
                                   is_examined_type=judge_type)

        # 写入表格
        if export_type == 'xls':
            output = io.BytesIO()
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Sheet1')
        else:
            output = io.BytesIO()
            wb = xlsxwriter.Workbook(output)
            wb.strings_to_formulas = False
            ws = wb.add_worksheet('Sheet1')

        rows = ['学年', '学号', '姓名', '班级', '申请类别', '申请大类', '申请分数', '申请理由', '照片', '审批状态', '审批意见']

        for index, content in enumerate(rows):
            ws.write(0, index, content)

        count = 1
        for apply in page_reply:
            ws.write(count, 0, apply.apply_year)
            ws.write(count, 1, apply.stu_id)
            ws.write(count, 2, apply.stu_name)
            ws.write(count, 3, apply.stu_class)
            ws.write(count, 4, apply.apply_type)
            ws.write(count, 5, apply.bonus_category.content)
            ws.write(count, 6, apply.apply_score)
            ws.write(count, 7, apply.activity)
            if apply.image:
                ws.write(count, 8, '有')
            else:
                ws.write(count, 8, '无')
            ws.write(count, 9, apply.examine_status)
            if apply.examine_content:
                ws.write(count, 10, apply.examine_content)
            else:
                ws.write(count, 10, '')

            count += 1

        filename = ''
        if year:
            filename += year
        if stu_class:
            filename += stu_class
            if stu_class == 'all':
                filename += '所有班级'
            else:
                filename += stu_class
        if stu_id:
            filename += stu_id
        if stu_name:
            filename += stu_name
        if judge_type:
            if judge_type == 'all':
                filename += '所有状态'
            else:
                filename += judge_type
        filename += '活动审批情况'

        filename = filename.encode('utf-8').decode('ISO-8859-1')

        if export_type == 'xls':
            wb.save(output)
            output.seek(0)
            response = HttpResponse(content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename={}.xls'.format(filename)
            response.write(output.getvalue())
        else:
            wb.close()
            output.seek(0)
            response = HttpResponse(content_type='application/ms-excel')
            # print(form.name)
            response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(filename)
            response.write(output.getvalue())

        return response
