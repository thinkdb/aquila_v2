from django.db import models

# Create your models here.


class Privileges(models.Model):
    auth_obj = models.CharField(max_length=50)
    select_host = models.SmallIntegerField()
    update_host = models.SmallIntegerField()
    insert_host = models.SmallIntegerField()
    delete_host = models.SmallIntegerField()

    select_user = models.SmallIntegerField()
    update_user = models.SmallIntegerField()
    delete_user = models.SmallIntegerField()
    insert_user = models.SmallIntegerField()

    pub_ince = models.SmallIntegerField()
    audit_ince = models.SmallIntegerField()

    select_data = models.SmallIntegerField()

    class Meta:
        db_table = 'auth_privileges'


class UserGroup(models.Model):
    user_group_name = models.CharField(max_length=50, unique=True)
    user_group_jd = models.CharField(max_length=50)

    class Meta:
        db_table = 'auth_user_group'


class UserRole(models.Model):
    role_name = models.CharField(max_length=50)
    comm = models.CharField(max_length=100)

    class Meta:
        db_table = 'auth_user_role'

    def __unicode__(self):
        return self.role_name, self.comm


class UserInfo(models.Model):
    user_name = models.CharField(max_length=50, unique=True)
    user_pass = models.CharField(max_length=96)
    email = models.EmailField()
    lock_flag = models.PositiveSmallIntegerField(default=0)
    role = models.ForeignKey(to=UserRole, related_query_name='user_role_r', db_constraint=False)
    user_group = models.ForeignKey('UserGroup', db_constraint=False)

    class Meta:
        db_table = 'auth_user_info'


class HostGroup(models.Model):
    host_group_name = models.CharField(max_length=50, unique=True)
    host_group_jd = models.CharField(max_length=50)

    class Meta:
        db_table = 'host_groups'

    def __unicode__(self):
        return self.host_group_jd


class AppType(models.Model):
    app_name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'app_type'

    def __unicode__(self):
        return self.app_name


class HostInfo(models.Model):
    host_ip = models.CharField(max_length=45, unique=True)
    app_type = models.ForeignKey(to='AppType', to_field='id', db_constraint=False)
    host_user = models.CharField(max_length=20)
    host_pass = models.CharField(max_length=30)
    host_port = models.SmallIntegerField()
    host_group = models.ForeignKey(to='HostGroup', to_field='id', db_constraint=False)

    class Meta:
        db_table = 'hosts_info'

    def __unicode__(self):
        return self.host_ip


class HostAPPAccount(models.Model):
    host = models.ForeignKey(to='HostInfo', to_field='id', db_constraint=False)
    app_user = models.CharField(max_length=20)
    app_pass = models.CharField(max_length=30)
    app_port = models.SmallIntegerField()

    class Meta:
        db_table = 'host_app_account'


# Inception
class InceptionWorkOrderInfo(models.Model):
    id = models.AutoField(primary_key=True)
    work_order_id = models.BigIntegerField(unique=True)
    work_user = models.CharField(max_length=50)
    db_host = models.CharField(max_length=45)
    db_name = models.CharField(max_length=50, default='test_db')
    end_time = models.DateTimeField(default='1980-01-01 01:01:01')
    review_user = models.CharField(max_length=50)
    review_time = models.DateTimeField(default='1980-01-01 01:01:01')
    review_status = models.SmallIntegerField(default=10)    # 10: None， 0: pass， 1:  reject
    work_status = models.SmallIntegerField(default=10)      # 10: None， 0: successfully， 1: fail, 2: queue， 3: running
    r_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ince_work_order_info'


class InceptionAuditDetail(models.Model):
    id = models.AutoField(primary_key=True)
    work_order = models.ForeignKey(to='InceptionWorkOrderInfo', on_delete=models.CASCADE,
                                   to_field='work_order_id', db_constraint=False)
    sql_sid = models.SmallIntegerField()              # sql_number
    status = models.SmallIntegerField()               # 0: None, 1: RERUN, 2: CHECKED, 3: EXECUTED
    err_id = models.SmallIntegerField()               # 0: None, 1: warnings, 2: error
    stage_status = models.SmallIntegerField()
    # 0: Audit completed,  1: Execute failed
    # 2: Execute Successfully
    # 3: Execute Successfully\nBackup successfully
    # 4: Execute Successfully\nBackup filed

    error_msg = models.TextField()                    # None, str,
    sql_content = models.TextField()                  # sql content
    aff_row = models.IntegerField()                   # affect_rows
    rollback_id = models.CharField(max_length=50)     # rollback_id
    backup_dbname = models.CharField(max_length=100)  # inception backup database name
    execute_time = models.IntegerField()              # sql running times，*1000 ms
    sql_hash = models.CharField(max_length=50, default='----')        # pt_osc
    r_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dbms_ince_audit_detail'


class InceAuditSQLContent(models.Model):
    id = models.AutoField(primary_key=True)
    work_order = models.ForeignKey('InceptionWorkOrderInfo', on_delete=models.CASCADE,
                                   to_field='work_order_id', db_constraint=False)
    sql_content = models.TextField()

    class Meta:
        db_table = 'ince_audit_sql_content'


class WorkOrderTask(models.Model):
    host_ip = models.CharField(max_length=45)
    app_user = models.CharField(max_length=20)
    app_pass = models.CharField(max_length=30)
    app_port = models.SmallIntegerField()
    wid = models.BigIntegerField(unique=True)
