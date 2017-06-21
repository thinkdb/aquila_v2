from django.shortcuts import render
from back.views.AuthAccount import AuthAccount, GetUserInfo


@AuthAccount
def index(request):
    user_info = GetUserInfo(request)
    return render(request, 'index.html', {'user_info': user_info})


def test(request):
    return render(request, 'test.html')