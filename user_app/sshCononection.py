import paramiko

class SSHConnection(object):

    def __init__(self, host='192.168.2.103', port=22, username='root',pwd='123456'):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd
        self.__k = None
        self.transport=None

    def connect(self):
        transport = paramiko.Transport((self.host,self.port))
        transport.connect(username=self.username,password=self.pwd)
        self.transport = transport

    def close(self):
        self.transport.close()

    def upload(self,local_path,target_path):
        # 连接，上传
        # file_name = self.create_file()
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        # 将location.py 上传至服务器 /tmp/test.py
        sftp.put(local_path, target_path)

    def download(self,remote_path,local_path):
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        sftp.get(remote_path,local_path)

    def cmd(self, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = self.transport
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)
        # 获取命令结果
        in_bash=stdin.read()
        result = stdout.read()
        err=stderr.read()
        # print (str(result,encoding='utf-8'))
        return result

# ssh = SSHConnection()
# ssh.connect()
# ssh.cmd("ls")
# ssh.upload('s1.py','/tmp/ks77.py')
# ssh.download('/tmp/test.py','kkkk',)
# ssh.cmd("df")
# ssh.close()