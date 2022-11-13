from django.urls import path,re_path
from . import views
from .views import *
app_name="background"
urlpatterns = [
    path("login_user/",views.login_user,name="login_user"),
    path("logout/",views.logout,name="logout"),
    path("",views.user_information.as_view(),name="index"),
    re_path("userinfodetial/(?P<pk>\d+)",views.user_information_detail.as_view(),name="userinfodetial"),
    path("input_file/",views.input_file.as_view(),name="input_file"),
    re_path("input_file/(?P<pk>\d+)",views.input_file_detail.as_view(),name="input_file"),
    path("output_file/",views.output_file.as_view(),name="output_file"),
    re_path("output_file/(?P<pk>\d+)",views.out_file_detail.as_view(),name="output_file"),
]