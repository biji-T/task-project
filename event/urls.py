from django.conf.urls import url
from django.urls import path, re_path
from . import views


app_name = 'event'

urlpatterns = [
    path('', views.EventListView.as_view(), name='home'),

]