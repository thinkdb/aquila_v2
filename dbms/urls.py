from django.conf.urls import url
from dbms.views import SQLpublish, MySQL_MetaData, RollBackWork, SQLquery

urlpatterns = [
    url(r'^sql_publish/sql-commit.html$', SQLpublish.SqlCommit.as_view(), name='SqlCommit'),
    url(r'^sql_publish/sql-audit.html$', SQLpublish.SqlAudit.as_view(), name='SqlAudit'),
    url(r'^sql_publish/sql-running.html$', SQLpublish.SqlRunning.as_view(), name='SqlRunning'),
    url(r'^sql_publish/sql-view.html$', SQLpublish.SqlView.as_view(), name='SqlView'),
    url(r'^sql_publish/sql-progress.html$', SQLpublish.SqlProgress.as_view(), name='SqlProgress'),

    url(r'^metadata/metadata_info.html', MySQL_MetaData.GetMetaData.as_view(), name='MySQLmetadata'),
    url(r'^metadata/collect_metadata.html', MySQL_MetaData.CollectMetadata.as_view(), name='CollectMetadata'),
    url(r'^metadata/get_table_info.html$', MySQL_MetaData.GetTableInfo.as_view(), name='GetTableInfo'),

    url(r'^rollback/get_rollback-(?P<wid>\d+).html', RollBackWork.RollBack.as_view(), name='Rollback'),

    url(r'^sqlquery.html$', SQLquery.SqlQuery.as_view(), name='SQLQuery'),
]
