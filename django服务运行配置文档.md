#### 环境配置

~~~shell
PyMySQL
django
djangorestframework
django-cors-headers
pandas
Pillow
paramiko
~~~



#### 数据库配置

> 位置：background>setting.py

~~~python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        #'NAME': BASE_DIR / 'db.sqlite3',
        'NAME': "model_data",
        'USER':"root",
        "PASSWORD":"nuocheng",
        "RORT":"3306",
        "HOST":"127.0.0.1"
    }
}
~~~



#### django数据库迁移

~~~python
python manager.py makemigrations
python manager.py migrate
~~~



#### 项目启动

~~~python
python manager.py runserver 0.0.0.0:8000
~~~



#### 虚拟机里的root密码设置与backadmin>sshCononection.py、user_app>sshCononection.py配置密码一样