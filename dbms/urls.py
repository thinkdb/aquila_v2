from django.conf.urls import url
from dbms.views import SQLpublish

urlpatterns = [
    url(r'^sql_publish/sql-commit.html$', SQLpublish.SqlCommit.as_view(), name='SqlCommit'),
    url(r'^sql_publish/sql-audit.html$', SQLpublish.SqlAudit.as_view(), name='SqlAudit'),
    url(r'^sql_publish/sql-running.html$', SQLpublish.SqlRunning.as_view(), name='SqlRunning'),
    url(r'^sql_publish/sql-view.html$', SQLpublish.SqlView.as_view(), name='SqlView'),
    url(r'^sql_publish/sql-detail-(?P<wid>\d+).html$', SQLpublish.SqlDetail.as_view(), name='SqlDetail'),

]
