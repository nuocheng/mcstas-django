#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 13:41:35 2022


用法：

1. 读取instr文件参数，显示到前端的instr参数域
a = Instr_Read(filename)
a.get_instr_para()
a.dict_para就是输出的参数,显示到instr参数那个区域

2. 用户修改参数后，把修改后的参数按照同样格式存在后台
dict_para_modified

3. 生成bash命令
kk = Bashline_Create(dirname,username)
kk.instr_bash(a.dict_para)
# GPU
kk.creat_bash_line(ncounts,instr_filename,core_type='GPU')
# CPU
kk.creat_bash_line(ncounts,instr_filename,core_type='CPU',ncores=10)


### bash 命令
后端服务器：拷贝文件到计算服务器

scp .instr mcstas@192.168.10.102:/home/mcstas/Documents/user1/  # self.path
scp xxx mcstas@192.168.10.102:/home/mcstas/Documents/user1/     # self.path

mcstas计算服务器端：执行计算

cd /home/mcstas/Documents/user1/   # self.path
mcrun xxxxxxx      # 也就是self.bashline


最终读取计算结果的文件夹：
self.path_data_out


@author: luowei
"""

'''
用户登录时的后台操作：
    1. 建立一份用户登录档案
    2. 分配一个计算服务器，临时保存计算服务器ip地址 
    3. 在该服务器的/home/mcstas/Documents/下建立用户名文件夹
        * 例如如果用户名为user1，建文件夹/home/mcstas/Documents/user1/

产生bash命令
 1. 读“instr文件参数修改”部分的参数和参数值，并转成python字典
 2. 将python字典转为命令
 3. 结合其他参数，输出bash命令，其他参数包括：
     * dirname：输出文件夹（例如test1）
         * 用户登录时，指定其计算服务器的的ip地址，例如为192.168.10.102
         * 在计算服务器上的默认完整文件路径：/home/mcstas/Documents/user1/test1/
     * file_instr : .instr文件的文件名
     * counts : 粒子计数
     * compute :
         * 显卡 : --openacc
         * cpu : '--mpi=%i' % (n_cpu)
    * kargs_string : .instr读出后修改的参数
        * 把dict变成vars = value的形式
    * username： user1
f'mcrun -c --mpi=%i %s -n %s -d %s %s' %(n_cpu,self.file_instr,counts,self.dirname,kargs_string)   

'''


'''
### bash 命令
后端服务器：拷贝文件到计算服务器

scp .instr mcstas@192.168.10.102:/home/mcstas/Documents/user1/  # self.path
scp xxx mcstas@192.168.10.102:/home/mcstas/Documents/user1/     # self.path

mcstas计算服务器端：执行计算

cd /home/mcstas/Documents/user1/   # self.path
mcrun xxxxxxx      # 也就是self.bashline


最终读取计算结果的文件夹：
self.path_data_out


'''


class Instr_Read():
    def __init__(self,filename):
        self.filename = filename
    
    #-------------------------------------------------------------
    # 从instr文件中读取输入参数
    def get_instr_para(self):
        self.get_instr_para_raw()
        self.dict_para = []
        for x in self.instr_para:
            self.dict_para.append(self.format_instr_para(x))
    
    def get_instr_para_raw(self):
        with open(self.filename, 'r') as f:
            junk = ''
            write = False
            while True:
                string = f.readline()   
                if not string:
                    break
                else:
                    if string.startswith('DEFINE INSTRUMENT'):
                        write = True
                    elif string.startswith('DECLARE'):
                        write = False
                        break
                if write:
                    string = string.split('//')[0] # 注释不计入
                    if len(string)>0:
                        junk  = junk + string.strip()
        f.close()
        print(junk)
        self.instr_para = junk.split('(')[1].split(')')[0].split(',')

    def format_instr_para(self,string):
        junk = string.strip().split('=')
        value=junk[1].strip()
        key = junk[0].split()[-1]
        if junk[0].split()[0] == 'string':
            value = value[1:-1]
        #else:
        #    value = eval(value)
        return {key:value}
    
class Bashline_Create():
    def __init__(self,dirname,username):
        path_default = '/home/mcstas/Documents/'
        # scp拷贝的目标文件夹
        self.dirname = dirname
        self.path = path_default+username
        # 计算输出文件的读取文件夹
        self.path_data_out = self.path+'/'+dirname
    
    def instr_bash(self,dict_para):
        string = ''
        for x in dict_para:
            string = string +'%s=%s ' % (list(x)[0],list(x.values())[0])
        self.instr_string = string
    
    def creat_bash_line(self,ncounts,instr_file,core_type='CPU',ncores=1):
        if core_type == 'CPU':
            self.bashline = 'mcrun -c --mpi==%i %s -d %s -n %i %s' % (ncores,instr_file,self.dirname,ncounts,self.instr_string)
        else:
            self.bashline = 'mcrun -c --openacc %s -d %s -n %i %s' % (instr_file,self.dirname,ncounts,self.instr_string)
        