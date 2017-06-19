import os
import sys
import django
from scripts.functions import DBAPI
current_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
path = os.path.dirname(current_path)
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] ='aquila_v2.settings'
django.setup()

from django.conf import settings


class Inception(object):
    def __init__(self, db_host, db_user, db_passwd, sql_content, db_port=3306):
        self.ince_host = getattr(settings, 'INCEPTION')['default']['INCEPTION_HOST']
        self.ince_port = int(getattr(settings, 'INCEPTION')['default']['INCEPTION_PORT'])
        self.host = db_host
        self.user = db_user
        self.passwd = db_passwd
        self.port = int(db_port)
        self.sql_content = sql_content
        self.execute = 0
        self.check = 1
        self.warnings = 0
        self.sql = None

    def montage_sql(self):
        self.sql = '/*--user=%s;--password=%s;--host=%s;--port=%s;--enable-check=%s;--enable-execute=%s;' \
                   '--enable-ignore-warnings=%s;--sleep=1;--enable-split=0;*/' \
                   'inception_magic_start;' \
                   '%s' \
                   'inception_magic_commit;' \
                   % (self.user, self.passwd, self.host, self.port,
                      self.check, self.execute, self.warnings, self.sql_content)

    def run_sql(self, warnings):
        self.execute = 1
        self.check = 0
        self.warnings = warnings
        self.montage_sql()
        try:
            conn = DBAPI(host=self.ince_host, user='', password='', port=self.ince_port)
            result = conn.conn_query(self.sql)
        except Exception as e:
            result = e

        return result

    def audit_sql(self):
        self.execute = 0
        self.check = 1
        self.montage_sql()
        conn = DBAPI(host=self.ince_host, user='', password='', port=self.ince_port)
        if conn.error:
            audit_result = {'status': 0, 'error': conn.error}
        else:
            audit_result = conn.conn_query(self.sql)
        return audit_result

# a = Inception(db_host='192.168.1.6', db_user='root', db_passwd='123456',
#     sql_content='use test; grant all privileges on *.* to "t"@"%" identified by "123";')
# ret = a.run_sql(0)
#
# print(ret)

