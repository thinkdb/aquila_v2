#!/bin/bash

#config monitor database server
monitor_db_host="192.168.1.6"
monitor_db_port=3306
monitor_db_user="root"
monitor_db_password="123456"
monitor_db_database="aquila2"

#config mysql server
mysql_client="/usr/local/mysql/bin/mysql"
mysql_host="192.168.1.10"
mysql_port=3306
mysql_user="root"
mysql_password="123456"

#config slowqury
slowquery_dir="/home/mysql/slow_log/"
slowquery_long_time=0.5
slowquery_file=`$mysql_client -h$mysql_host -P$mysql_port -u$mysql_user -p$mysql_password  -e "show variables like 'slow_query_log_file'"|grep log|awk '{print $2}'`
pt_query_digest="/usr/local/bin/pt-query-digest"

#config server_id
hostname=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d 'addr:'`



#collect mysql slowquery log into monitor database

$pt_query_digest \
--user=$monitor_db_user --password=$monitor_db_password --port=$monitor_db_port \
--review h=$monitor_db_host,D=$monitor_db_database,t=mysql_slow_query_review  \
--history h=$monitor_db_host,D=$monitor_db_database,t=mysql_slow_query_review_history  \
--no-report --limit=100% \
--filter="\$event->{Bytes} = length(\$event->{arg}) and \$event->{hostname}=\"$hostname\" " \
$slowquery_file > /tmp/analysis_slow_query.log

##### set a new slow query log ###########
tmp_log=`$mysql_client -h$mysql_host -P$mysql_port -u$mysql_user -p$mysql_password -e "select concat('$slowquery_dir','slowquery_',date_format(now(),'%Y_%m_%d_%H_%i'),'.log');"|grep log|sed -n -e '2p'`

#config mysql slowquery
$mysql_client -h$mysql_host -P$mysql_port -u$mysql_user -p$mysql_password -e "set global slow_query_log=1;set global long_query_time=$slowquery_long_time;"
$mysql_client -h$mysql_host -P$mysql_port -u$mysql_user -p$mysql_password -e "set global slow_query_log_file = '$tmp_log'; "

#delete log before 7 days
/usr/bin/find $slowquery_dir -name 'slowquery_*' -mtime +7|xargs rm -rf ;

####END####