from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from .sshCononection import SSHConnection
import json
import os
from background.settings import BASE_DIR
from backadmin.models import *
from channels.generic.websocket import AsyncWebsocketConsumer
import paramiko
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
CONSUMER_OBJECT_LIST = []

class sshConsumer(WebsocketConsumer):
    def connect(self):
        self.username = "msc"  # 临时固定用户名
        print('WebSocket建立连接：', self.username)
        # 直接从用户指定的通道名称构造通道组名称
        self.channel_group_name = 'msg_%s' % self.username

        # 加入通道层
        # async_to_sync(…)包装器是必需的，因为ChatConsumer是同步WebsocketConsumer，但它调用的是异步通道层方法。(所有通道层方法都是异步的。)
        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name,
            self.channel_name
        )

        # 接受WebSocket连接。
        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                'type': 'get_message',
            }
        )

    def disconnect(self, close_code):
        print('WebSocket关闭连接')
        # 离开通道
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

        # 从WebSocket中接收消息

    def receive(self, text_data=None, bytes_data=None):
        # print('WebSocket接收消息：', text_data, type(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # print("receive message",message,type(message))
        # 发送消息到通道
        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                'type': 'get_message',
                'message': message,
                "bash":text_data_json['bash'],
                "username":text_data_json['username'],
                "userid":text_data_json['userid'],
                "download_dir":text_data_json['download_dir'],
                "file":text_data_json['file_id'],
                "dirname":text_data_json['dirname']
            }
        )

        # 从通道中接收消息

    def get_message(self, event):
        # print("event",event,type(event))
        if event.get('message'):
            message = event['message']
            # 判断消息
            if message == "close":
                # 关闭websocket连接
                self.disconnect(self.channel_group_name)
                print("前端关闭websocket连接")

            # 判断消息，执行脚本
            if message == "start":
                # 执行的命令或者脚本
                bash = event['bash']
                username=event['username']
                userid=event['userid']
                file=event['file']
                scp_path2=event['download_dir']
                dirname=event['dirname']
                userdemo=userInformation.objects.get(name=username,pk=userid)
                ipconfig=userdemo.ipconfig

                # 远程连接服务器
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ipconfig, username="mcstas", password="chopper")
                # 务必要加上get_pty=True,否则执行命令会没有权限
                # stdin, stdout, stderr = ssh.cmd(bash)
                stdin, stdout, stderr = ssh.exec_command(bash,get_pty=True,bufsize=-1)
                # stdin, stdout, stderr = ssh.exec_command("bash /opt/test.sh",get_pty=True)
                # print(stdout.read())

                # result = stdout.read()
                # 循环发送消息给前端页面
                while True:
                    nextline = stdout.readline().strip()  # 读取脚本输出内容
                    self.send(
                        text_data=nextline
                    )
                    print("已发送消息:%s" % nextline)

                    if 'Placing instr file copy' in nextline:
                        break
                    if 'not found' in nextline:
                        break

                # while True:
                #     nextline = stderr.readline().strip()  # 读取脚本输出内容
                #     self.send(
                #         text_data=nextline
                #     )
                #     print("已发送消息:%s" % nextline)
                #     # 判断消息为空时,退出循环
                #     if not nextline:
                #         break

                # self.send(
                #     text_data=(str(stderr.read(),encoding='utf-8'))
                # )
                # print("报错消息:%s" % str(stderr.read(),encoding='utf-8'))
                # ssh.close()  # 关闭ssh连接
                    # 关闭websocket连接
                ssh.close()



                ssh = SSHConnection(host=ipconfig, username="root", pwd="DtwfDVe3NpFnJA4")
                ssh.connect()
                #将文件进行保存
                stdin,output1,stderr = ssh.cmd("ls {}".format(scp_path2))
                # print(output1.read())
                # output1=str(output1.read(),encoding="utf-8")
                # print(output1)
                output1=output1.read().decode()
                output2 = output1.split()
                print("output2")
                print(output2[1:])
                output2=output2[1:]
                output = [i for i in output2 if i != ""]

                if len(output)!=0:
                    print("当前文件夹下的内容")
                    print(output)
                    output_path = []
                    for item in output:
                        output_path.append(
                            '/home/{}/mcstas/Documents/{}/{}/{}'.format(userdemo.name, userdemo.name, dirname, item))

                    # 返回生成的文件进行保存到本服务器上
                    # 为用户创建在static/下创建用户文件/次数
                    user_download_path = os.path.join(BASE_DIR, "static", userdemo.name, str(userdemo.count))
                    if not os.path.exists(user_download_path):
                        os.makedirs(user_download_path)

                    file_demo=updateFile.objects.get(pk=file)
                    for item in output_path:
                        name = item.split("/")[-1]
                        ssh.download(item, os.path.join(BASE_DIR, "static", userdemo.name, str(userdemo.count), name))
                        mainFile.objects.create(userid=userdemo, fileid=file_demo,
                                                output_file="{}/{}/{}".format(userdemo.name, str(userdemo.count),
                                                                              name))  # --------------
                    # 远程连接结束
                ssh.close()
                self.disconnect(self.channel_group_name)
                print("后端关闭websocket连接")