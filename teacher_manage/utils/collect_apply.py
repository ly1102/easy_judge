# -*- coding:utf-8 -*-
# date: 2017-09-19 18:52
import os
import sys
import requests
from django.core.wsgi import get_wsgi_application
import threading
from bs4 import BeautifulSoup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_manage.settings")
sys.path.append(os.path.dirname(__file__))
application = get_wsgi_application()
from operation.models import BonusCategory, Apply, BonusDetail
from utils.conn_operation import get_conn_cookies, store_conn_cookies


class Crawler(threading.Thread):
    def __init__(self, conn, page_queue):
        threading.Thread.__init__()
        self.conn = conn
        self.page_queue = page_queue

    def run(self):
        pass


