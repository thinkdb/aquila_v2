from django.conf.urls import url
from back.views.account import Login

urlpatterns = [
    url(r'^login.html$', Login.as_view())
]