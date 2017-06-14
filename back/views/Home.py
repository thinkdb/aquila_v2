from django.shortcuts import render
from back.views.AuthAccount import AuthAccount


@AuthAccount
def index(request):
    return render(request, 'index.html', {'user_name': request.session['username']})
