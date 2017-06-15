#!/bin/env python3
# _*_ coding:utf8 _*_
import os
import sys
import django
from scripts import functions


current_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
path = os.path.dirname(current_path)
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] ='aquila_v2.settings'
django.setup()

from model_model import models

# init UserRole
models.UserRole.objects.create(id=1, role_name='admin', comm='超级管理员')
models.UserRole.objects.create(id=2, role_name='users', comm='普通员工,默认值')
models.UserRole.objects.create(id=3, role_name='qa', comm='测试')
models.UserRole.objects.create(id=4, role_name='dev', comm='开发')
models.UserRole.objects.create(id=5, role_name='dba', comm='数据库管理员')


# init UserGroup
models.UserGroup.objects.create(id=1, user_group_name='admin_group', user_group_jd='管理员组')
models.UserGroup.objects.create(id=2, user_group_name='default_group', user_group_jd='普通用户组, 默认组')
models.UserGroup.objects.create(id=3, user_group_name='dba_group', user_group_jd='数据库管理员组')

# init HostGroup
models.HostGroup.objects.create(id=1, host_group_name='db', host_group_jd='数据主机组')
models.HostGroup.objects.create(id=2, host_group_name='java', host_group_jd='java主机组')


# init AppType
models.AppType.objects.create(id=1, app_name='MySQL')
models.AppType.objects.create(id=2, app_name='Java')


# init privileges
models.Privileges.objects.create(
    id=1,
    auth_obj='admin_group',
    select_host=1,
    update_host=1,
    insert_host=1,
    delete_host=1,

    select_user=1,
    update_user=1,
    delete_user=1,
    insert_user=1,

    pub_ince=1,
    audit_ince=1,
    select_data=1
)
models.Privileges.objects.create(
    id=2,
    auth_obj='default_group',
    select_host=1,
    update_host=0,
    insert_host=0,
    delete_host=0,

    select_user=0,
    update_user=0,
    delete_user=0,
    insert_user=0,

    pub_ince=1,
    audit_ince=0,
    select_data=1
)

# init administrator
pass_str = functions.py_password('123456')
models.UserInfo.objects.create(
    id=1,
    user_name='admin',
    user_pass=pass_str,
    email='996846239@qq.com',
    role_id=1,
    user_group_id=1,
    lock_flag=0
)
