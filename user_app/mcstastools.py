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
from background.settings import BASE_DIR
import os,base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants as scipy_cons

m_value = scipy_cons.physical_constants['neutron mass'][0]  # kg
meV = scipy_cons.eV / 10 ** 3  #



class Instr_Read():
    def __init__(self, filename):
        self.filename = filename

    # -------------------------------------------------------------
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
                    string = string.split('//')[0]  # 注释不计入
                    if len(string) > 0:
                        junk = junk + string.strip()
        f.close()
        print(junk)
        self.instr_para = junk.split('(')[1].split(')')[0].split(',')

    def format_instr_para(self, string):
        junk = string.strip().split('=')
        value = junk[1].strip()
        key = junk[0].split()[-1]
        if junk[0].split()[0] == 'string':
            value = value[1:-1]
        # else:
        #    value = eval(value)
        return {key: value}


class Bashline_Create():
    def __init__(self, dirname, username):
        path_default = '/home/mcstas/Documents/'
        # scp拷贝的目标文件夹
        self.dirname = dirname
        self.path = path_default + username
        # 计算输出文件的读取文件夹
        self.path_data_out = self.path + '/' + dirname

    def instr_bash(self, dict_para):
        string = ''
        for x in dict_para:
            string = string + '%s=%s ' % (list(x)[0], list(x.values())[0])
        self.instr_string = string

    def creat_bash_line(self, ncounts, instr_file, core_type='CPU', ncores=1):
        if core_type == 'CPU':
            self.bashline = 'mcrun -c --mpi==%i %s -d %s -n %i %s' % (
            ncores, instr_file, self.dirname, ncounts, self.instr_string)
        else:
            self.bashline = 'mcrun -c --openacc %s -d %s -n %i %s' % (
            instr_file, self.dirname, ncounts, self.instr_string)


# ======================================================================================
def select_interp(x, df, index_x='', index_y=''):
    # linear interpolate
    # must sort values first !!!!
    data = df.sort_values(by=index_x).copy()
    return np.interp(x, data[index_x], data[index_y])


def select_from_sections(x, df, index_x=''):
    # select single energy data
    junk = df.loc[x <= df[index_x]]
    return junk.iloc[0]


# ======================================================================================
def split_first(string, sep=':'):
    # split方法的扩展,只split第一个sep，同时都strip处理
    junk_s = string.split(sep)
    junk1 = junk_s[1]
    for i in range(len(junk_s) - 2):
        junk1 = junk1 + sep + junk_s[i + 2]
    return [junk_s[0].strip(), junk1.strip()]


class Read_Simu():
    # 读取mcstas模拟数据中的mccode.sim文件信息
    def __init__(self, filename):
        self.filename = filename
        self.read_index()
        self.read_simu()

    def read_simu(self):
        info = {}
        info['header'] = self.read_dict(0)
        info['instrument'] = self.read_dict(1)
        info['simulation'] = self.read_dict(2)
        # read data
        for i in range(self.n_ind - 3):
            junk = self.read_dict(i + 3)
            info[junk['component']] = junk
        self.info = info

    def read_index(self):
        f = open(self.filename, 'r')
        self.junk_se = pd.Series(f.readlines())
        index = self.junk_se[self.junk_se == '\n'].index.values
        ind_end = np.array(list(index[1:] - 1) + [len(self.junk_se) - 1])
        self.n_ind = len(index) + 1

        self.ind_title = [0] + list(index + 1)
        self.ind_dict = [[1, 2]]
        for i in range(self.n_ind - 1):
            self.ind_dict = self.ind_dict + [[index[i] + 2, ind_end[i] - 1]]
        f.close()

    def read_dict(self, ind_numb):
        # ind_numb : 0,1,2,...
        header = {}
        key = ''
        value = ''
        ind_start = self.ind_dict[ind_numb][0]
        ind_end = self.ind_dict[ind_numb][1] + 1
        #
        for i in range(ind_start, ind_end):
            junk_string = split_first(self.junk_se[i])
            if key == junk_string[0]:
                value = value + ' ; ' + junk_string[1]
            else:
                key = junk_string[0]
                value = junk_string[1]
            header[key] = value
        return header

    def list_data(self, index='filename'):
        data = []
        for x in list(self.info.keys())[3:]:
            data.append(self.info[x][index])
        return data


# ======================================================================================
class Read_Mcstas():
    def __init__(self, filename):
        self.filename = filename
        self.read_header()
        self.read_data()

    def read_header(self):
        header = {}
        f = open(self.filename, 'r')
        for line in f:
            if '# ' in line:
                if '# Data' in line:
                    break
                name = line.split(':')[0].strip().split(' ')[1]
                header[name] = line.split(':')[-1].strip()
        f.close()
        header['data_dimension'] = eval(header['type'].split('_')[1][0])
        if header['data_dimension'] == 2:
            bin_x = header['type'].split(',')[0].split('(')[1].strip()
            bin_y = header['type'].split(',')[1].split(')')[0].strip()
            header['bins'] = [int(bin_x), int(bin_y)]
            junk = [float(x) for x in header['xylimits'].split(' ')]
            header['xlimit'] = junk[:2]
            header['ylimit'] = junk[2:]
            header['step_x'] = (header['xlimit'][1] - header['xlimit'][0]) / (header['bins'][0] - 1)
            header['step_y'] = (header['ylimit'][1] - header['ylimit'][0]) / (header['bins'][1] - 1)
        elif header['data_dimension'] == 1:
            bin_x = header['type'].split('(')[1].split(')')[0].strip()
            header['bins'] = [int(bin_x)]
            header['xlimit'] = [float(x) for x in header['xlimits'].split(' ')]
        header['variables'] = header['variables'].split(' ')
        # header['date'] = header['Directory'].split('/')[-1].split('_')[-2]
        # header['id'] = header['Directory'].split('/')[-1].split('_')[-1]
        self.header = header

    def read_data(self):
        if self.header['data_dimension'] == 2:
            columns_n = self.header['bins'][0]
            self.data = pd.read_csv(self.filename, sep='\s+', comment='#', index_col=None,
                                    names=np.linspace(0, columns_n - 1, columns_n))
        elif self.header['data_dimension'] == 1:
            self.data = pd.read_csv(self.filename, sep='\s+', comment='#', index_col=None,
                                    names=self.header['variables'])

    def select_data(self, variable=0):
        self.variable = variable
        self.data_select = self.data.iloc[
                           self.header['bins'][1] * variable:self.header['bins'][1] * (variable + 1)].values
        self.mx, self.my = np.mgrid[
            slice(self.header['xlimit'][0], self.header['xlimit'][1] + self.header['step_x'], self.header['step_x']),
            slice(self.header['ylimit'][0], self.header['ylimit'][1] + self.header['step_y'], self.header['step_y'])]
        self.x = self.mx.transpose()[0]
        self.y = self.my[0]

    def plot_2d(self, set_clim=-1, variable=0, log=False):
        self.select_data(variable=variable)
        self.data_plot = self.data_select
        if log:
            self.data_plot = np.log(self.data_plot)
            minvalue = np.min(self.data_plot)
            self.data_plot[np.isinf(self.data_plot)] = minvalue
        if set_clim != -1:
            plt.pcolormesh(self.mx, self.my, self.data_plot.transpose(), cmap='jet', vmin=set_clim[0], vmax=set_clim[1])
        else:
            plt.pcolormesh(self.mx, self.my, self.data_plot.transpose(), cmap='jet')
        cbar = plt.colorbar()
        cbar.set_label(self.header['variables'][variable])
        plt.xlabel(self.header['xlabel'])
        plt.ylabel(self.header['ylabel'])
        plt.savefig(os.path.join(BASE_DIR,'static','2d.png'))
        str_html = self.path2base64(os.path.join(BASE_DIR, 'static', '2d.png'))
        return str_html

        # title_text = '%s_%s.%s' %(self.header['date'],self.header['id'],self.header['filename'])
        # plt.title(title_text)

    def plot_1d(self, xran=False, **kargs):
        self.data_plot = self.data
        index_x = self.header['variables'][0]
        if xran:
            self.data_plot = self.data[self.data[index_x] > xran[0]][self.data[index_x] < xran[1]]
        x = self.data_plot[index_x]
        y = self.data_plot['I']
        dy = self.data_plot['I_err']
        plt.errorbar(x, y, yerr=dy, fmt='o-', **kargs)
        plt.xlabel(index_x)
        plt.ylabel('I')
        plt.savefig(os.path.join(BASE_DIR, 'static', '1d.png'))
        str_html=self.path2base64(os.path.join(BASE_DIR, 'static', '1d.png'))
        return str_html

    def plot(self):
        if self.header['data_dimension'] == 2:
            return self.plot_2d()
        elif self.header['data_dimension'] == 1:
            return self.plot_1d()
    def path2base64(self,path):
        with open(path, "rb") as f:
            byte_data = base64.b64encode(f.read())
            base64_str = str(byte_data, encoding="utf-8")
            html_str = "data:image/jpg;base64," + base64_str
        print("进入编辑页面")
        return html_str

class Read_Mcstas_nd(Read_Mcstas):

    def __init__(self, filename):
        name_str = 'p x y z vx vy vz t sx sy sz I'
        self.columns_name = name_str.split()
        Read_Mcstas.__init__(self, filename)

    def read_data(self):
        self.data = pd.read_csv(self.filename, sep='\s+', comment='#', index_col=None, names=self.columns_name)
        self.data['div_x'] = self.data['vx'] * 180 / self.data['vz'] / np.pi
        self.data['div_y'] = self.data['vy'] * 180 / self.data['vz'] / np.pi
        self.data['v2'] = self.data['vx'] ** 2 + self.data['vy'] ** 2 + self.data['vz'] ** 2
        self.data['e'] = m_value * self.data['v2'] / 2.0 / meV  # meV
        self.data['lamb'] = 9.045 / np.sqrt(self.data['e'])

    def plot_2d(self, ind=['x', 'y'], bins_value=[20, 20], weights='N', set_clim=-1):
        if weights == 'N':
            plt.hist2d(self.data[ind[0]], self.data[ind[1]], bins=bins_value, cmap='jet', vmin=set_clim[0],
                       vmax=set_clim[1])
        else:
            plt.hist2d(self.data[ind[0]], self.data[ind[1]], bins=bins_value, cmap='jet', weights=self.data[weights],
                       vmin=set_clim[0], vmax=set_clim[1])
        plt.xlabel(ind[0])
        plt.ylabel(ind[1])
        plt.colorbar().set_label(weights)

    def plot_1d(self, ind='x', bins_value=20, weights='I'):
        # p也处理成I
        self.data_hist = pd.DataFrame()
        data = np.histogram(self.data[ind], bins=bins_value, weights=self.data[weights])
        self.data_hist[ind] = (data[1][1:] + data[1][:-1]) / 2
        self.data_hist['I'] = data[0]
        data = np.histogram(self.data[ind], bins=bins_value)
        self.data_hist['N'] = data[0]
        self.data_hist['I_err'] = self.data_hist['I'] / np.sqrt(self.data_hist['N'])
        plt.plot(self.data_hist[ind], self.data_hist['I'], 'o-')
        plt.xlabel(ind)
        plt.ylabel('I')


# ======================================================================================
def lambda_to_e(lamb):
    return (9.045 / lamb) ** 2