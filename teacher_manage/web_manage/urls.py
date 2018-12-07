"""web_manage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from web_manage.settings import MEDIA_ROOT
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from django.views.generic.base import RedirectView
from operation.views import LoginView, ApplyListView, ApplyInitView, UserOperation, ClassView,\
    ClearDataView, ExitLoginView, GetNewDataView, YearView, ExportView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', LoginView.as_view(), name="login"),
    url(r'^UserLogin\.html$', RedirectView.as_view(url='/'), name='error_index'),
    url(r'^shenpi$', ApplyListView.as_view(), name="apply_list"),
    url(r'^init$', ApplyInitView.as_view(), name="apply_init"),
    url(r'^classes$', ClassView.as_view(), name="classes"),
    url(r'^years$', YearView.as_view(), name="years"),
    url(r'^operation$', UserOperation.as_view(), name="user_operation"),
    url(r'^flush_db$', ClearDataView.as_view(), name="flush"),
    url(r'^logout$', ExitLoginView.as_view(), name="logout"),
    url(r'^get_new_data$', GetNewDataView.as_view(), name="get_new_data"),
    url(r'^export$', ExportView.as_view(), name="export"),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'/image/static/favicon.ico')),
    # 配置上传文件的访问处理
    url(r'^image/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

]
