from django.conf.urls import url
from back.views import account

urlpatterns = [
    url(r'^login.html$', account.Login.as_view(), name='login'),
    url(r'^register.html$', account.Register.as_view(), name='register'),

]