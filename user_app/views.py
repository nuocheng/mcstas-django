from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse
import json
from .sshCononection import SSHConnection as ssh
import numpy as np
import paramiko
import hashlib
import time
import string
import pandas as pd
import os
from .mcstastools import *
from collections import defaultdict
from backadmin.models import *
from background.settings import BASE_DIR
# Create your views here.
#文件目录生成
def make_dis(username):
    path=os.path.join(BASE_DIR,'static','upload',username)
    if not os.path.exists(path):
        os.mkdir(path)
    #在目录下生成5个csv文件
    data={
        "name":['nuocheng','xiaoming','xiaohong'],
        "gender":['man','woman','man'],
        "age":[11,34,29],
        'math':[100,96,95],
        "english":[75,86,45],
        "history":[80,76,92]
    }
    data_info=pd.DataFrame(data=data)
    path1 = os.path.join(BASE_DIR, 'static', 'upload', username,'1.csv')
    path2 = os.path.join(BASE_DIR, 'static', 'upload', username,'2.csv')
    path3 = os.path.join(BASE_DIR, 'static', 'upload', username,'3.csv')
    data_info.to_csv(path1,index=0)
    data_info.to_csv(path2,index=0)
    data_info.to_csv(path3,index=0)
    path1='{}/1.csv'.format(username)
    path2='{}/2.csv'.format(username)
    path3='{}/3.csv'.format(username)
    return [path1,path2,path3]



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
    return redirect(reverse("user:login_user"))

def get_user(request):
    username=request.headers.get("username")
    id=request.headers.get("id")
    flag=request.headers.get("flag")
    return userInformation.objects.get(name=username, pk=id, stat=flag)

#判断是否已经进行了登录的修饰器
def exist_user_login(func):
    def exist_next(request):
        token=request.headers.get("token")
        if token:
            return func(request)
        else:
            return JsonResponse({"message":"您还没有登录，请进行登录进行获取数据信息！"})
    return exist_next

#获取用户提交的所有keyword
@exist_user_login
def get_user_keyword(request):
    if request.method=='GET':

        userdemo=get_user(request)
        output_list=outputFile.objects.filter(userid=userdemo)
        info_list=[]
        for item in output_list:
            info={
                "id":item.id,
                "keyword":item.keyword,
                "create_at":item.create_at
            }
            info_list.append(info)
        return JsonResponse({"info":info_list})

#数据下载
@exist_user_login
def users_download_data(request):
    if request.method=='GET':
        userdemo=get_user(request)
        id=request.GET.get("id")
        file_str=mainFile.objects.get(userid=userdemo,id=id)
        return JsonResponse({"file":"http://127.0.0.1:8000/static/upload/"+str(file_str.output_file)})

#权限请求
@exist_user_login
def users_columns_data(request):
    if request.method=='GET':
        userdemo=get_user(request)
        if userdemo.stat!=0:
            zero_menu=[
                {
                    'path': "/fuzhu",
                    'name': "user",
                    'lable': "辅助系统",
                    'icon': "user",
                    'url': "userManage/userManage"
                },
                {
                    'path': "/xianka",
                    'name': "user",
                    'lable': "显卡计算平台",
                    'icon': "user",
                    'url': "userManage/userManage"
                },
                {
                    'label': "数据",
                    'icon': "location",
                    'children': [
                        {
                            'path': "/otherone",
                            'name': "page1",
                            'lable': "数据操作",
                            'icon': "setting",
                            'url': "other/pageOne"
                        },
                    ]
                }
            ]
        else:
            zero_menu = [
                {
                    'path': "/fuzhu",
                    'name': "user",
                    'lable': "辅助系统",
                    'icon': "user",
                    'url': "userManage/userManage"
                },
                {
                    'path': "/xianka",
                    'name': "user",
                    'lable': "显卡计算平台",
                    'icon': "user",
                    'url': "userManage/userManage"
                },

            ]
        return JsonResponse({"info":zero_menu})

#参数添加
@exist_user_login
def add_user_keyword(request):
    if request.method=='POST':
        userdemo = get_user(request)
        keyword = request.POST.get("keyword")
        json_info = keyword
        outputFile.objects.create(userid=userdemo, keyword=str(json_info))
        userdemo.count+=1
        userdemo.save()
        output_list = outputFile.objects.filter(userid=userdemo)
        info_list=[]
        for item in output_list:
            info={
                "id":item.id,
                "keyword":item.keyword,
                "create_at":item.create_at
            }
            info_list.append(info)
        return JsonResponse({"info":info_list})


#参数的删除
@exist_user_login
def del_user_keyword(request):
    if request.method == 'GET':

        userdemo = get_user(request)
        keyword = request.GET.get("kid")
        outputFile.objects.get(pk=keyword,userid=userdemo).delete()
        output_list = outputFile.objects.filter(userid=userdemo)
        info_list = []
        for item in output_list:
            info = {
                "id": item.id,
                "keyword": item.keyword,
                "create_at": item.create_at
            }
            info_list.append(info)
        return JsonResponse({"info": info_list})

#用户上传参数文件
@exist_user_login
def update_file_user(request):
    if request.method=='POST':
        userdemo = get_user(request)
        file=request.FILES.get("file")
        file_demo=updateFile.objects.create(userid=userdemo,inputfile=file)
        try:
            #读取文件
            filename=os.path.join(BASE_DIR,"static",'upload',str(file_demo.inputfile))
            a = Instr_Read(filename)
            a.get_instr_para()
            return JsonResponse({"data":a.dict_para,"fileid":file_demo.pk,"flag":1})
        except:
            file_demo.delete()
            return JsonResponse({"flag":0})

#多文件上传
@exist_user_login
def update_many_file_user(request):
    if request.method=='POST':
        userdemo = get_user(request)
        file_list=request.FILES.getlist("file")
        file_info=[]
        for item in file_list:
            file_demo=updateFile.objects.create(userid=userdemo,inputfile=item)
            info={
                "id":file_demo.pk,
                "name":str(file_demo.inputfile),
                "create":file_demo.create_at
            }
            file_info.append(info)
        #返回上传的信息

        return JsonResponse({"info":file_info,"flag":1})

#文件的删除
@exist_user_login
def delete_many_file_user(request):
    if request.method=='GET':
        userdemo = get_user(request)
        id=request.GET.get("id")
        update_demo=updateFile.objects.get(pk=id,userid=userdemo)
        update_demo.delete()
        file_info=[]
        for item in updateFile.objects.get(userid=userdemo,flag=0):
            info={
                "id":item.pk,
                "name":str(item.inputfile),
                "create":item.create_at
            }
            file_info.append(info)
        #返回上传的信息
        return JsonResponse({"info":file_info})




#用户参数更改并运行
@exist_user_login
def users_update_data_run(request):
    if request.method=='POST':
        userdemo = get_user(request)
        #------------------------数据库获取
        username=userdemo.name
        mcstas_ip=userdemo.ipconfig
        scp_path='/home/mcstas/Documents/{}/'.format(userdemo.name)
        #-----------------用户上传
        fileid=request.POST.get("fileid")
        dirname=request.POST.get("dirname")
        scp_path2 = '/home/mcstas/Documents/{}/{}/'.format(userdemo.name,dirname)
        ncounts=request.POST.get("ncounts")
        core_type = request.POST.get("core_type")
        ncores = request.POST.get("ncores")
        #------------------------------------------------------后期参数可能会进行修改-------
        #获取该文件名
        file=updateFile.objects.get(pk=fileid,userid=userdemo,flag=0)
        instr_file=str(file.inputfile).split('/')[-1]
        path=os.path.join(BASE_DIR,'static','upload',str(file.inputfile))
        a = Instr_Read(path)
        a.get_instr_para()
        para_list = a.dict_para
        b = Bashline_Create(dirname, username)
        b.instr_bash(para_list)
        b.creat_bash_line(ncounts, instr_file, core_type=core_type, ncores=ncores)
        mingling=b.bashline  #最终命令
        #远程连接
        con=ssh(host=mcstas_ip,port=22,username='root',pwd="123456")
        #首先创建一个用户文件夹
        con.cmd("mkdir -p {}".format(scp_path))
        #创建用户指定文件夹
        con.cmd("mkdir -p {}".format(scp_path2))
        #首先进行将服务器上文件scp上传到模型服务器上
        user_file=updateFile.objects.filter(userid=userdemo,flag=0)
        path_list=[]
        for item in user_file:
            path_list.append(os.path.join(BASE_DIR,'static','upload',str(item.inputfile)))

        for item in path_list:
            fname=item.split("/")[-1]
            con.upload(item,'/home/mcstas/Documents/{}/'.format(userdemo.name))
        # 将上传的文件标记为1
        updateFile.objects.filter(userid=userdemo, flag=0).update(flag=1)
        #在模型服务器上运行模型bash命令
        con.cmd("cd /home/mcstas/Documents/{}/".format(userdemo.name))
        #接收控制台输出
        con.cmd(mingling)
        #将生成的文件下载到本地
        output=con.cmd("cd {}".format(scp_path2))
        output_path=[]
        for item in output:
            output_path.append('/home/mcstas/Documents/{}/{}/{}'.format(userdemo.name,dirname,item))
        #返回生成的文件进行保存到本服务器上
        #为用户创建在static/下创建用户文件/次数
        user_download_path=os.path.join(BASE_DIR,"static",userdemo.username,str(userdemo.count))
        if not os.path.exists(user_download_path):
            os.mkdir(user_download_path)
        for item in output_path:
            con.download(item,user_download_path)
            name=item.split("/")[-1]
            mainFile.objects.create(userid=userdemo,fileid=file,output_file="{}/{}/{}".format(userdemo.username,str(userdemo.count),name))  #--------------
        # 远程连接结束
        ssh.close()
        #将文件列表进行返回
        main_file_list=mainFile.objects.filter(userid=userdemo,fileid=file)
        file_list=[]
        # print(main_file_list)
        for item in main_file_list:
            info={
                "id":item.pk,
                "username":item.userid.name,
                "fileid_name":str(item.fileid.inputfile),
                "output_file":item.output_file
            }
            file_list.append(info)
        return JsonResponse({"data":file_list})

#用户点击数据进行数据可视化
@exist_user_login
def users_run_data(request):
    if request.method=='GET':
        userdemo = get_user(request)
        file_id=request.GET.get("id")
        get_file=mainFile.objects.get(userid=userdemo,pk=file_id)
        file_path=os.path.join(BASE_DIR,'static','upload',str(get_file.output_file))
        #pandas进行读取文件
        data=pd.read_csv(file_path)
        json_data=data.to_json(orient ="records")
        info={
            "name":data['name'].tolist(),
            "math":data['math'].tolist(),
            "english":data['english'].tolist(),
            "history":data['history'].tolist()
        }
        return JsonResponse({"data":json.loads(str(json_data)),"figure":info})


@exist_user_login
def users_run_all_data(request):
    if request.method=='GET':
        userdemo = get_user(request)
        main_file_list = mainFile.objects.filter(userid=userdemo)
        file_list = []
        # print(main_file_list)
        for item in main_file_list:
            info = {
                "id": item.pk,
                "username": item.userid.name,
                "fileid_name": str(item.fileid.inputfile),
                "output_file": item.output_file
            }
            file_list.append(info)
        return JsonResponse({"data": file_list})

@exist_user_login
def users_deal_data(request):
    if request.method == 'GET':
        userdemo = get_user(request)
        file_id = request.GET.get("id")
        get_file = mainFile.objects.get(userid=userdemo, pk=file_id)
        get_file.delete()
        main_file_list = mainFile.objects.filter(userid=userdemo)
        file_list = []
        for item in main_file_list:
            info = {
                "id": item.pk,
                "username": item.userid.name,
                "fileid_name": str(item.fileid.inputfile),
                "output_file": item.output_file
            }
            file_list.append(info)
        return JsonResponse({"data": file_list})
#用户登录
def login_user(request):
    if request.method=='POST':
        username=request.POST.get("username")
        password=request.POST.get("password")
        # print(username)
        if userInformation.objects.filter(name=username,password=password).exists():
            user_demo=userInformation.objects.filter(name=username,password=password).first()
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
            if user_demo.stat==0:
                #表示用户登录
                return JsonResponse({"message":"success","flag":0,"code":0,"token":token,"username":username,"id":user_demo.id})
            else:
                return JsonResponse({"message":"success","flag":1,"code":0,"token":token,"username":username,"id":user_demo.id})
        else:
            return JsonResponse({"message":"error","flag":-1})
    else:
        return render(request,"user/login.html")


def index(request):
    if exist_login(request):
        if request.method=='GET':
            user_demo=get_login_user(request)
            return render(request,"user/index.html",context={
                "user":user_demo
            })
    else:
        return redirect(reverse("user:login_user"))

def welcome(request):
    if exist_login(request):
        if request.method=='GET':
            return render(request,"user/welcome1.html")
        else:
            """
            关键字出现的形式为字典类型
            """
            keyword = request.POST.get("keyword")
            keyword_list=keyword.split("}")
            keyword_list=list(map(lambda x:x+"}",keyword_list[:-1]))
            keywords=[]
            for item in keyword_list:
                keywords.append(json.loads(item))
            if len(keywords)!=0:
                keyword_json=defaultdict(dict)
                for demo in keywords:
                    deal_demo=demo
                    info={
                        deal_demo['keyword']:{
                            deal_demo['props']: deal_demo['value']
                        }
                    }
                    keyword_json[deal_demo['keyword']][deal_demo['props']] = deal_demo['value']
                # print(keyword_json)
                user_demo = get_login_user(request)
                demo = outputFile.objects.create(userid=user_demo, keyword=keyword_json)
                """
                加载模型，出现图片,并将显示的图片地址进行返回
                """
                return JsonResponse({"imgurl": demo.output_file,"message":json.dumps(keyword_json)})
            else:
                return JsonResponse({ "message": "您提交的数据为空"})
    else:
        return redirect(reverse("user:login_user"))
def welcome2(request):
    if exist_login(request):
        if request.method=='GET':
            return render(request,"user/welcom21.html")
        else:
          pass
    else:
        return redirect(reverse("user:login_user"))