from django.shortcuts import redirect
from dbms import models
from django.db.models import Q


def AuthAccount(func):
    def inner(request, *args, **kwargs):
        username = request.session.get('username', None)
        ret = models.UserInfo.objects.filter(Q(user_name=username) | Q(email=username)).count()
        if not username and not ret:
            return redirect('/back/login.html')
        return func(request, *args, **kwargs)
    return inner


def GetUserInfo(request):
    '''
    get user privileges, group privileges
    '''
    username = request.session.get('username', None)
    q = models.UserInfo.objects.filter(Q(user_name=username) | Q(email=username)).all().select_related('role', 'user_group')
    print(q)
    pass