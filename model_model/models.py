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


class RoleInfo(models.Model):
    role_name = models.CharField(max_length=50, unique=True)
    comm = models.CharField(max_length=100)

    class Meta:
        db_table = 'auth_role_info'

    def __unicode__(self):
        return self.role_name, self.comm


class UserInfo(models.Model):
    user_name = models.CharField(max_length=50, unique=True)
    user_pass = models.CharField(max_length=96)
    email = models.EmailField()
    lock_flag = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'auth_user_info'

    def __unicode__(self):
        return self.user_name


class UserRoleRelationship(models.Model):
    role = models.ForeignKey(RoleInfo, db_constraint=False, db_index=True)
    user = models.ForeignKey(UserInfo, db_constraint=False, db_index=True)

    class Meta:
        db_table = 'user_role_relationship'


class UserGroupRelationship(models.Model):
    user = models.ForeignKey(UserInfo, db_constraint=False, db_index=True)
    group = models.ForeignKey('UserGroup', db_constraint=False, db_index=True)

    class Meta:
        db_table = 'user_group_relationship'


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
    app_type = models.ForeignKey(to='AppType', to_field='id', db_constraint=False, db_index=True)
    host_user = models.CharField(max_length=20)
    host_pass = models.CharField(max_length=30)
    host_port = models.SmallIntegerField()
    host_group = models.ForeignKey(to='HostGroup', to_field='id', db_constraint=False, db_index=True)

    class Meta:
        db_table = 'hosts_info'

    def __unicode__(self):
        return self.host_ip


class HostAPPAccount(models.Model):
    host = models.ForeignKey(to='HostInfo', to_field='id', db_constraint=False, db_index=True)
    app_user = models.CharField(max_length=20)
    app_pass = models.CharField(max_length=30)
    app_port = models.SmallIntegerField()

    class Meta:
        db_table = 'host_app_account'


# ============================= Inception =============================
class InceptionWorkOrderInfo(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(max_length=100, default='test')
    work_title = models.CharField(max_length=60)
    work_order_id = models.BigIntegerField(unique=True)
    work_user = models.CharField(max_length=50)
    db_host = models.CharField(max_length=45)
    master_host = models.CharField(max_length=45, default='----')
    db_name = models.CharField(max_length=50, default='test_db')
    end_time = models.DateTimeField(default='1980-01-01 01:01:01')
    review_user = models.ForeignKey(UserInfo, db_constraint=False)
    review_time = models.DateTimeField(default='1980-01-01 01:01:01')
    review_status = models.SmallIntegerField(default=10)    # 10: None， 0: pass， 1:  reject
    work_status = models.SmallIntegerField(default=10)
    # 10: None， 1: successfully， 0: fail, 2: queue， 3: running, 4:cancel, 5: 部分成功

    work_run_time = models.DateTimeField(default='1980-01-01 01:01:01')
    work_cron_time = models.DateTimeField(default='1980-01-01 01:01:01')
    comm = models.CharField(max_length=500, default='----')
    review_comm = models.CharField(max_length=500, default='----')
    r_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ince_work_order_info'
        index_together = (['work_user', 'review_status'], ['review_user', 'review_status'])


class InceptionAuditDetail(models.Model):
    id = models.AutoField(primary_key=True)
    flag = models.SmallIntegerField(default=1)   # 1: audit, 2: running 3: over
    work_order = models.ForeignKey(to='InceptionWorkOrderInfo', on_delete=models.CASCADE,
                                   to_field='work_order_id', db_constraint=False, db_index=True)
    sql_sid = models.SmallIntegerField()              # sql_number
    status = models.CharField(max_length=30)
    status_code = models.SmallIntegerField()
    # Audit
    # 0: Successfully,  1: Warning, 2: Error, 7: 审核完成

    # Execute
    # 3: 执行失败, 4: 执行成功, 5: 执行成功,备份成功, 6: 执行成功,备份失败

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
                                   to_field='work_order_id', db_constraint=False, db_index=True)
    sql_content = models.TextField()

    class Meta:
        db_table = 'ince_audit_sql_content'


class WorkOrderTask(models.Model):
    host_ip = models.CharField(max_length=45)
    db_name = models.CharField(max_length=50, default='test_db')
    app_user = models.CharField(max_length=20)
    app_pass = models.CharField(max_length=30)
    app_port = models.SmallIntegerField(default=3306)
    work_order = models.OneToOneField('InceptionWorkOrderInfo', on_delete=models.CASCADE,
                                      to_field='work_order_id', db_constraint=False, unique=True)
    work_status = models.SmallIntegerField(default=10)  # 10 None, 1 run, 4 cancle
    audit_status = models.SmallIntegerField(default=10)  # 10 None, 0: pass, 1: reject

    class Meta:
        db_table = 'work_order_tasks'


# class AppVersion(models.Model):
#     version = models.CharField()
#     r_time = models.DateTimeField(auto_now_add=True)


# ============================= MySQL MetaData =============================
class MetaDataTables(models.Model):
    host_ip = models.CharField(max_length=50)
    table_schema = models.CharField(max_length=64)
    table_name = models.CharField(max_length=64)
    engine = models.CharField(max_length=64)
    row_format = models.CharField(max_length=10)
    table_rows = models.BigIntegerField()
    avg_row_length = models.BigIntegerField()
    max_data_length = models.BigIntegerField()
    data_length = models.BigIntegerField()
    index_length = models.BigIntegerField()
    data_free = models.BigIntegerField()
    chip_size = models.BigIntegerField()
    auto_increment = models.BigIntegerField(default=0)
    table_collation = models.CharField(max_length=32)
    create_time = models.DateTimeField(null=True)
    update_time = models.DateTimeField(null=True)
    check_time = models.DateTimeField(null=True)
    table_comment = models.CharField(max_length=500)
    table_md5 = models.CharField(max_length=100)

    class Meta:
        db_table = 'mysql_metadata_tables'
        unique_together = ('table_name', 'table_schema', 'host_ip')

    def __unicode__(self):
        return self.table_schema, self.table_name


class MetaDataColumns(models.Model):
    host_ip = models.CharField(max_length=50)
    table_schema = models.CharField(max_length=64)
    table_name = models.CharField(max_length=64)
    column_name = models.CharField(max_length=64)
    column_type = models.CharField(max_length=64)
    collation_name = models.CharField(max_length=32)
    is_nullable = models.CharField(max_length=3, default='---')
    column_key = models.CharField(max_length=3, default='---')
    column_default = models.CharField(max_length=150, default='----')
    extra = models.CharField(max_length=30, default='----')
    privileges = models.CharField(max_length=80)
    column_comment = models.CharField(max_length=500, default='----')
    column_md5 = models.CharField(max_length=100)

    class Meta:
        db_table = 'mysql_metadata_columns'
        index_together = ('table_name', 'table_schema', 'host_ip')

    def __unicode__(self):
        return self.table_schema, self.table_name


class MetaDataIndexs(models.Model):
    host_ip = models.CharField(max_length=50)
    table_schema = models.CharField(max_length=64)
    table_name = models.CharField(max_length=64)
    column_name = models.CharField(max_length=64)
    non_unique = models.SmallIntegerField()
    index_name = models.CharField(max_length=64)
    seq_in_index = models.SmallIntegerField()
    cardinality = models.BigIntegerField(default=0)
    nullable = models.CharField(max_length=3)
    index_type = models.CharField(max_length=16)
    index_comment = models.CharField(max_length=500)
    index_md5 = models.CharField(max_length=100)

    class Meta:
        db_table = 'mysql_metadata_indexs'
        index_together = ('table_name', 'table_schema', 'host_ip')

    def __unicode__(self):
        return self.table_schema, self.table_name


class MetaDataProcedure(models.Model):
    host_ip = models.CharField(max_length=50)
    schema_name = models.CharField(max_length=64)
    routine_name = models.CharField(max_length=64)
    routine_type = models.CharField(max_length=9)
    create_time = models.DateTimeField()
    last_altered = models.DateTimeField()

    class Meta:
        db_table = 'mysql_metadata_procedure'
        index_together = ('routine_name', 'schema_name', 'host_ip')

    def __unicode__(self):
        return self.schema_name, self.routine_name


class GetMetaDataError(models.Model):
    host_ip = models.CharField(max_length=50)
    error_msg = models.CharField(max_length=1000)
    r_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'get_metadata_error'


class MetaDataTableStructure(models.Model):
    table = models.OneToOneField(MetaDataTables, db_constraint=False, unique=True)
    content = models.TextField()

    class Meta:
        db_table = 'mysql_metadata_table_structure'


class MetaDataProcedureStructure(models.Model):
    procedure = models.OneToOneField(MetaDataProcedure, db_constraint=False, unique=True)
    content = models.TextField()

    class Meta:
        db_table = 'mysql_metadata_procedure_structure'


class MetaDataDatabase(models.Model):
    host_ip = models.CharField(max_length=50)
    schema_name = models.CharField(max_length=64)
    default_character_set_name = models.CharField(max_length=32)
    default_collation_name = models.CharField(max_length=32)
    db_md5 = models.CharField(max_length=100)

    class Meta:
        db_table = 'mysql_metadata_database'
