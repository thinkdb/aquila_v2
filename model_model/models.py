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
