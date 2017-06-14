from django.conf.urls import url
from back.views.account import Login, Register
from back.views import Home

urlpatterns = [
    url(r'^login.html$', Login.as_view(), name='login'),
    url(r'^register.html$', Register.as_view(), name='register'),
    url(r'^index.html$', Home.index, name='index'),

]