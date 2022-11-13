from .models import *
import json
from django.http import JsonResponse
from rest_framework.response import Response
from .serializers import UpdateFileSerializer,UserInformationSerializer,OutputFileSerializer
from django.shortcuts import render
from rest_framework.views import APIView
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
