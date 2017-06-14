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

    def __str__(self):
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

