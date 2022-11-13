from django.urls import path,re_path
from . import views
from .views import *
app_name="user"
urlpatterns = [
    path("login/",views.login_user,name="login_user"),
    path("logout/",views.logout,name="logout"),
    path("get_user_keyword/",views.get_user_keyword,name="get_user_keyword"),
    path("add_user_keyword/",views.add_user_keyword,name="add_user_keyword"),
    path("del_user_keyword/",views.del_user_keyword,name="del_user_keyword"),
    path("update_file_user/",views.update_file_user,name="update_file_user"),
    path("users_update_data_run/",views.users_update_data_run,name="users_update_data_run"),
    path("",views.index,name="index"),
    path("welcome/",views.welcome,name="welcome"),
    path("welcome2/",views.welcome2,name="welcome2"),

]