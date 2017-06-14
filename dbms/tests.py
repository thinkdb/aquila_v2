from django.test import TestCase

from dbms import models
from django.db.models import Q
# Create your tests here.

q = models.UserInfo.objects.filter(Q(user_name='admin') | Q(email='admin')).all().select_related('role', 'user_group')
print(q)