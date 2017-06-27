from django.conf.urls import url
from dbms.views import SQLpublish, MySQL_MetaData

urlpatterns = [
    url(r'^sql_publish/sql-commit.html$', SQLpublish.SqlCommit.as_view(), name='SqlCommit'),
    url(r'^sql_publish/sql-audit.html$', SQLpublish.SqlAudit.as_view(), name='SqlAudit'),
    url(r'^sql_publish/sql-running.html$', SQLpublish.SqlRunning.as_view(), name='SqlRunning'),
    url(r'^sql_publish/sql-view.html$', SQLpublish.SqlView.as_view(), name='SqlView'),
    url(r'^sql_publish/sql-detail-(?P<wid>\d+).html$', SQLpublish.SqlDetail.as_view(), name='SqlDetail'),
    url(r'^metadata/metadata_info.html', MySQL_MetaData.GetMetaData.as_view(), name='MySQLmetadata'),
    url(r'^metadata/collect_metadata.html', MySQL_MetaData.CollectMetadata.as_view(), name='CollectMetadata')
]
