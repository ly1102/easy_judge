# -*- coding:utf-8 -*-
# date: 2017-09-20 19:59
from bs4 import BeautifulSoup
import re


class LoginPage:
    def __init__(self, page_content):
        self.soup = BeautifulSoup(page_content, 'lxml', from_encoding="gbk")

    def get_captcha_url(self):
        src = self.soup.find('img', border="0")
        url = src['src']
        print(url)
        return "xsc.cuit.edu.cn/Sys/" + url

    def get_all_hidden_input(self):
        all_hidden_input = self.soup.find_all("input", type="hidden")
        input_dict = {}
        for h_input in all_hidden_input:
            try:
                input_dict[h_input['name']] = h_input['value']

            except Exception as e:
                print(e)
            # print(h_input['name'], h_input['value'])
        return input_dict

    def get_login_ok_alert(self):
        alert = self.soup.find('script')
        # print(alert)
        if "alert" in str(alert):
            return alert
        return ''


class ApplyListPage:
    def __init__(self, page_content):
        self.soup = BeautifulSoup(page_content, 'lxml', from_encoding='gbk')

    def get_next_page_form(self):
        all_input = self.soup.find_all('input')
        page_form = {}
        for each_input in all_input:
            try:
                key, value = each_input['name'], each_input['value']
                if 'Btn' in key:
                    continue
                if 'IsCheck' in key:
                    continue
                # print()
                page_form[key] = value
            except KeyError:
                key = each_input['name']
                # print('no value---', key)
                page_form[key] = ''
        page_form['FDYStatus'] = '0'
        page_form['ClassNo'] = ''
        page_form['__EVENTTARGET'] = 'GridView1'
        # page_form['__VIEWSTATE'] = ''
        # page_form['BtnSearch'] = '查 询'.encode('gbk')
        # for k, v in page_form.items():
        #     print(k, v)
        return page_form

    def get_all_apply_href(self):
        table = self.soup.find('table', id="GridView1")
        all_href = []
        for a_tag in table.find_all('a'):
            href = a_tag['href']
            if 'javascript' in href:
                continue
            full_href = 'http://xsc.cuit.edu.cn/Sys/SystemForm/StudentJudge/' + href
            all_href.append(full_href)
            # print(full_href)
            # print(a_tag.text)
        # print(len(all_href))
        return all_href

    def get_max_page_num(self):
        notice = self.soup.find('div', id="DGNotice")
        text = notice.text.strip()
        max_page_text = re.search(r'共\d+页', text).group()
        max_page_num = re.search(r'\d+', max_page_text).group()
        # print(max_page_text, max_page_num)
        try:
            return int(max_page_num)
        except Exception as e:
            print(e)
            return 1


class ApplyPage:
    def __init__(self, page_content):
        self.soup = BeautifulSoup(page_content, 'lxml', from_encoding='gbk')

    def get_stu_id(self):
        stu_id = self.soup.find('span', id="StudentInfo1_StudentId").text
        # print(stu_id)
        return stu_id

    def get_stu_name(self):
        stu_name = self.soup.find('span', id="StudentInfo1_Name").text
        # print(stu_name)
        return stu_name

    def get_stu_class(self):
        stu_class = self.soup.find('span', id="StudentInfo1_ClassNo").text
        # print(stu_class)
        return stu_class

    def get_apply_type(self):
        apply_type = self.soup.find('span', id="ObjectInfo1_TypeName").text
        # print(apply_type)
        return apply_type

    def get_is_add_score(self):
        is_add = self.soup.find('span', id="ObjectInfo1_AddOrSub").text
        # print(is_add)
        if '加分' not in is_add:
            return False
        else:
            return True

    def get_apply_year(self):
        apply_year = self.soup.find('span', id="ObjectInfo1_YearTime").text
        # print(apply_year)
        return apply_year

    def get_apply_content(self):
        try:
            apply_content = self.soup.find('input', id="ObjectInfo1_ActionThing")['value']
            # print(apply_content)
            return apply_content
        except Exception as e:
            print(e)
            return ''

    def get_apply_bonus(self):
        select = self.soup.find('select', id="ObjectInfo1_ObjectList")
        # print(select)
        # self.soup.has_key()
        if select:
            for option in select.find_all('option'):
                # print(option)
                if "selected" in str(option):
                    two_bonus = option['value']
                    text = option.text
                    # print(two_bonus, text)
                    return two_bonus.strip().split('-')
        else:
            bonus = self.soup.find('span', id="ObjectInfo1_NumNo").text.strip()
            return [bonus]

    def get_apply_default_score(self):
        score_tag = self.soup.find('input', id="ObjectInfo1_Score")
        if score_tag:
            score = score_tag['value']
            # print(score)
            return score
        else:
            return None

    def get_apply_score(self):
        # 当是选项且无法更改分数时，该选项无法找到，返回None
        try:
            apply_score = self.soup.find('span', id="ObjectInfo1_Credit").text
            # print(apply_content)
            return apply_score
        except Exception as e:
            return self.get_apply_default_score()

    def get_apply_image(self):
        """http://xsc.cuit.edu.cn/Sys/DownLoad/StudentJudge/201791210590028aebac7bb5a4932be213f77739a2587.jpg"""
        img_div = self.soup.find('div', id="ObjectInfo1_ImgDiv1")
        if img_div:
            img = img_div.find('img')
            src = img['src']
            full_src = src.replace('../..', 'http://xsc.cuit.edu.cn/Sys')
            full_src = full_src.replace('\\', '/')
            # print(full_src)
            return full_src
        else:
            return None

    def get_judge_status(self):
        judge_status = self.soup.find('span', id="FDYStatus").text.strip()
        # print(judge_status)
        return judge_status

    def get_judge_content(self):
        judge_content = self.soup.find('textarea', id='FDYThing').text.strip()
        return judge_content

    def get_inputs(self):
        all_input = {}
        for each_input in self.soup.find_all('input'):
            try:
                key = each_input['name']
                value = each_input['value']
                # print(key, "---", value)
                if key == '__VIEWSTATE':
                    all_input[key] = value
                if key == '__VIEWSTATEGENERATOR':
                    all_input[key] = value
            except KeyError:
                # print(each_input['name'])
                pass
        return all_input

    def get_alert_status(self):
        alert = self.soup.find('script')
        if '成功' in str(alert):
            return True
        else:
            return alert.text


def open_page_test(file_name):
    with open(file_name, 'r', encoding='utf-8') as fp:
        read = fp.read()
        apply_page = ApplyPage(read)
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
        apply_default_score = apply_page.get_apply_default_score()
        inputs = apply_page.get_inputs()
        print('\n'.join([stu_id, stu_name, stu_class, apply_type, apply_year, str(is_add_score),
                         activity, apply_image, apply_status, apply_default_score]))
        print(bonus)
        print(inputs)



# open_page_test('apply.html')
# print('------------------------')
# open_page_test('apply_no_select.html')
# print('------------------------')
# open_page_test('apply_no_image.html')
# open_page_test('apply_form_select.html')


# fp = open('../templates/login.html', encoding="gbk")
# read = fp.read()
# fp.close()
# login_page = LoginPage(read)
# login_page.get_captcha_url()
# login_page.get_all_hidden_input()

# with open('loginok.html', 'r', encoding='utf-8') as fp:
#     read = fp.read()
#     soup = BeautifulSoup(read, 'lxml')
#     print(soup.find('script'))


# with open('apply_list.html', 'r', encoding='utf-8') as fp:
#     read = fp.read()
#     page = ApplyListPage(read)
#     max_page_num = page.get_max_page_num()
#     all_href = page.get_all_apply_href()
#     for i in all_href:
#         print(i)


