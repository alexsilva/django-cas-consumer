from django.conf.urls import include, url

from .views import *

urlpatterns = [
    url(r'^login/', login, name="cas_login"),
    url(r'^logout/', logout, name="cas_logout"),
]
