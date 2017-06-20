from django.conf.urls import url
from cmdb.views import CMDBManage

urlpatterns = [
    url(r'^host/manage.html$', CMDBManage.HostManage.as_view(), name='HostManage'),
    url(r'^hostgroup/manage.html$', CMDBManage.HostGroupManage.as_view(), name='HostGroupManage'),

    url(r'^user/manage.html$', CMDBManage.UserManage.as_view(), name='UserManage'),
    url(r'^usergroup/manage.html$', CMDBManage.UserGroupManage.as_view(), name='UserGroupManage'),

    url(r'^privileges/manage.html$', CMDBManage.PrivManage.as_view(), name='PrivManage'),
    url(r'^privilegesgroup/manage.html$', CMDBManage.PrivGroupManage.as_view(), name='PrivGroupManage'),


]