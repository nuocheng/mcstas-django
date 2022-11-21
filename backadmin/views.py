from .models import *
import json
from django.http import JsonResponse
from rest_framework.response import Response
from .serializers import UpdateFileSerializer,UserInformationSerializer,OutputFileSerializer
from django.shortcuts import render
from .models import *
import hashlib
import time
from rest_framework.views import APIView
from .sshCononection import SSHConnection
from rest_framework.generics import GenericAPIView
# Create your views here.
#用户的登录与注册

#判断用户是否登录
def exist_login(request):
    username=request.session.get("username")
    userid=request.session.get("id")
    stat=request.session.get("stat")
    return userInformation.objects.filter(name=username,pk=userid,stat=stat).exists()
#登录后返回登录对象
def get_login_user(request):
    username = request.session.get("username")
    userid = request.session.get("id")
    stat = request.session.get("stat")
    return userInformation.objects.get(name=username, pk=userid, stat=stat)
#用户退出登录
def logout(request):
    request.session.flush()
    return Response()


#用户登录
def login_user(request):
    if request.method=='POST':
        username=request.POST.get("username")
        password=request.POST.get("password")
        if userInformation.objects.filter(name=username,password=password).exists():
            user_demo=userInformation.objects.filter(name=username,password=password).first()
            request.session['id']=user_demo.pk
            request.session['username']=user_demo.name
            request.session['stat']=user_demo.stat
            if user_demo.stat==0:
                return JsonResponse({"message":"success","flag":0})
            else:
                return JsonResponse({"message":"success","flag":1})
        else:
            return JsonResponse({"message":"error","flag":-1})
    else:
        return render(request,"admin/login.html")



#管理员获取用户列表
class user_information(GenericAPIView):
    queryset = userInformation.objects
    serializer_class = UserInformationSerializer
    def get(self,request):
        # if exist_login(request):
            serializer=self.get_serializer(instance=self.get_queryset(),many=True)
            return Response(serializer.data)
        # else:
        #     return JsonResponse({"meg":"请先登录"})
    def post(self,request):
        # if exist_login(request):
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        # else:
        #     return JsonResponse({"meg":"请先登录"})

class user_information_detail(GenericAPIView):
    queryset = userInformation.objects
    serializer_class = UserInformationSerializer
    def get(self,request,pk):
        # if exist_login(request):
            serializer=self.get_serializer(instance=self.get_object(),many=False)
            return Response(serializer.data)
        # else:
        #     return JsonResponse({"meg": "请先登录"})
    def put(self,request,pk):
        # if exist_login(request):
            serializer=self.get_serializer(instance=self.get_object(),data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        # else:
        #     return JsonResponse({"meg": "请先登录"})
    def delete(self,request,pk):
        # if exist_login(request):
            self.get_object().delete()
            return Response()
        # else:
        #     return JsonResponse({"meg": "请先登录"})

class input_file(GenericAPIView):
    queryset = updateFile.objects
    serializer_class = UpdateFileSerializer
    def get(self,request):
        # if exist_login(request):
            serializer=self.get_serializer(instance=self.get_queryset(),many=True)
            return Response(serializer.data)
        # else:
        #     return JsonResponse({"meg": "请先登录"})

    def post(self,request):
        # if exist_login(request):
            serializer=self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        # else:
        #     return JsonResponse({"meg": "请先登录"})

class input_file_detail(GenericAPIView):
    queryset = updateFile.objects
    serializer_class = UpdateFileSerializer

    def get(self,request,pk):
        # if exist_login(request):
            serializer = self.get_serializer(instance=self.get_object(), many=False)
            return Response(serializer.data)
        # else:
        #     return JsonResponse({"meg": "请先登录"})

    def put(self,request,pk):
        # if exist_login(request):
            serializer = self.get_serializer(instance=self.get_object(),data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        # else:
        #     return JsonResponse({"meg": "请先登录"})

    def delete(self,request,pk):
        # if exist_login(request):
            self.get_object().delete()
            return Response()
        # else:
        #     return JsonResponse({"meg": "请先登录"})

class output_file(GenericAPIView):

        queryset = outputFile.objects
        serializer_class = OutputFileSerializer
        def get(self,request):
            # if exist_login(request):
                serializer=self.get_serializer(instance=self.get_queryset(),many=True)
                return Response(serializer.data)
            # else:
            #     return JsonResponse({"meg": "请先登录"})
        def post(self,request):
            # if exist_login(request):
                serializer=self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(serializer.errors)
            # else:
            #     return JsonResponse({"meg": "请先登录"})


class out_file_detail(GenericAPIView):
    queryset = outputFile.objects
    serializer_class = OutputFileSerializer

    def get(self,request,pk):
        # if exist_login(request):
            serializer = self.get_serializer(instance=self.get_object(), many=False)
            return Response(serializer.data)
        # else:
        #     return JsonResponse({"meg": "请先登录"})

    def put(self,request,pk):
        # if exist_login(request):
            serializer = self.get_serializer(instance=self.get_object(),data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        # else:
        #     return JsonResponse({"meg": "请先登录"})

    def delete(self,request,pk):
        # if exist_login(request):
            self.get_object().delete()
            return Response()
        # else:
        #     return JsonResponse({"meg": "请先登录"})


#判断是否已经进行了登录的修饰器
def exist_user_login(func):
    def exist_next(request):
        token=request.headers.get("token")
        if token:
            if get_user(request):
                return func(request)
            else:
                return JsonResponse({"message": "您没有权限！"})
        else:
            return JsonResponse({"message":"您还没有登录，请进行登录进行获取数据信息！"})
    return exist_next

def get_user(request):
    username=request.headers.get("username")
    id=request.headers.get("id")
    flag=request.headers.get("flag")
    return userInformation.objects.get(name=username, pk=id, stat=2)

#管理员获取用户信息
@exist_user_login
def admin_get_user_info(request):
    if request.method=='GET':
        admindemo=get_user(request)
        userinfo=userInformation.objects.filter(stat__in=[0,1])
        info_list=[]
        for item in userinfo:
            info={
                'id':item.id,
                "name":item.name,
                "password":item.password,
                "ipconfig":item.ipconfig,
                "count":item.count,
                "create_at":item.create_at,
            }
            info_list.append(info)
        return JsonResponse({"data":info_list})


@exist_user_login
def admin_get_one_user_info(request):
    if request.method == 'GET':
        admindemo = get_user(request)
        id=request.GET.get("id")
        userinfo = userInformation.objects.filter(stat__in=[0, 1],pk=id)
        info_list = []
        for item in userinfo:
            info = {
                'id': item.id,
                "name": item.name,
                "password": item.password,
                "ipconfig": item.ipconfig,
                "count": item.count,
                "create_at": item.create_at,
            }
            info_list.append(info)
        return JsonResponse({"data": info_list})

#管理员添加用户信息
@exist_user_login
def admin_add_user_info(request):
    if request.method == 'POST':
        admindemo = get_user(request)
        username=request.POST.get("username")
        password=request.POST.get("password")
        ipconfig=request.POST.get("ipconfig")
        stat=int(request.POST.get("stat"))
        user_demo=userInformation.objects.create(name=username,password=password,ipconfig=ipconfig,stat=stat)
        #管理员在相应的主机上创建用户账号
        # ssh=SSHConnection(host=user_demo.ipconfig,port=22,username="root",pwd="12345678")
        ssh = SSHConnection(host=user_demo.ipconfig)
        try:
            ssh.connect()
            ssh.cmd("adduser {}".format(user_demo.name))
            ssh.add_user("passwd {}".format(user_demo.name),pwd=str(user_demo.name)*3)
            return JsonResponse({"flag": 1, "message": "创建成功"})
        except:
            return JsonResponse({"flag":0,"message":"连接失败，请确保该主机已开启，root密码错误或者22号端口号没有开放"})

@exist_user_login
def admin_change_user_info(request):
    if request.method == 'POST':
        admindemo = get_user(request)
        id=request.POST.get("id")
        # username = request.POST.get("username")
        password = request.POST.get("password")
        ipconfig = request.POST.get("ipconfig")
        stat = int(request.POST.get("stat"))
        user_demo=userInformation.objects.filter(pk=id)
        if user_demo[0].ipconfig==ipconfig:
            user_demo.update(password=password,stat=stat)
            return JsonResponse({"flag": 1, "message": "修改成功"})
        else:
            user_demo.update(password=password, ipconfig=ipconfig, stat=stat)
            # ssh = SSHConnection(host=user_demo.ipconfig, port=22, username="root", pwd="12345678")
            ssh = SSHConnection(host=user_demo.ipconfig, port=22, username='root', pwd="DtwfDVe3NpFnJA4")
            try:
                ssh.connect()
                ssh.cmd("adduser {}".format(user_demo.name))
                ssh.add_user("passwd {}".format(user_demo.name), pwd=str(user_demo.name) * 3)
                return JsonResponse({"flag": 1, "message": "修改成功"})
            except:
                return JsonResponse({"flag": 0, "message": "连接失败，请确保该主机已开启，root密码错误或者22号端口号没有开放"})

@exist_user_login
def admin_delete_user_info(request):
    if request.method == 'GET':
        id = request.GET.get("id")
        print(id)
        user_demo = userInformation.objects.get(pk=id)
        user_demo.delete()
        return JsonResponse({"flag": 1, "message": "删除成功"})


#管理员登录
def login_admin(request):
    if request.method=='POST':
        username=request.POST.get("username")
        password=request.POST.get("password")
        if userInformation.objects.filter(name=username,password=password,stat=2).exists():
            user_demo=userInformation.objects.filter(name=username,password=password,stat=2).first()
            #token设计
            request.session.set_expiry(3600 * 4)
            md5 = hashlib.md5()
            md5.update((username + password + "1258" + str(time.time())).encode())
            token = md5.hexdigest()
            #
            request.session['id']=user_demo.pk
            request.session['username']=user_demo.name
            request.session['stat']=user_demo.stat
            request.session['token']=token

            return JsonResponse({"message":"success","flag":1,"code":0,"token":token,"username":username,"id":user_demo.id})
        else:
            return JsonResponse({"message":"error","flag":-1})