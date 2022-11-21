from django.db import models

# Create your models here.
class userInformation(models.Model):
    id=models.AutoField("用户ID",primary_key=True)
    name=models.CharField("用户名称",max_length=50,null=False,blank=False)
    password=models.CharField("用户密码",max_length=30,null=False,blank=False)
    filesize=models.FloatField("用户文件大小",null=False,blank=False,default=0.0)
    ipconfig=models.CharField(max_length=225,default="192.168.10.102",null=True,blank=True)
    stat=models.IntegerField(choices=((0,"普通用户"),(1,"管理员"),(2,"超级管理员")),default=0)
    count=models.IntegerField(default=0)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table="userinformation"

#用户上传的文件
class updateFile(models.Model):
    id = models.AutoField(primary_key=True)
    userid=models.ForeignKey(userInformation,on_delete=models.CASCADE,related_name="userinputfile")
    inputfile=models.FileField(upload_to="%Y%m%d/")
    flag=models.IntegerField(choices=((0,"未使用"),(1,"已使用")),default=0)
    create_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="inputfile"

class outputFile(models.Model):
    id=models.AutoField(primary_key=True)
    userid=models.ForeignKey(userInformation,on_delete=models.CASCADE,related_name="useroutfile")
    fileid=models.ForeignKey(updateFile,on_delete=models.SET_NULL,related_name="updatefileid",null=True,blank=True)
    keyword=models.TextField(null=True,blank=True)
    output_file=models.CharField(max_length=255,null=True,blank=True)
    create_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="outputfile"
#生成文件
class mainFile(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.ForeignKey(userInformation, on_delete=models.CASCADE, related_name="mainoutfile")
    fileid = models.ForeignKey(updateFile, on_delete=models.CASCADE, related_name="mainfileid", null=True,
                               blank=True)
    output_file = models.CharField("生成的文件",max_length=255, null=True, blank=True)
    class Meta:
        db_table="mainfirstfile"

class secondFile(models.Model):
    id = models.AutoField(primary_key=True)
    secondfileid=models.ForeignKey(mainFile,on_delete=models.CASCADE,related_name="secondfile")
    secondoutput_file=models.CharField("二次对应生成的文件",max_length=255, null=True, blank=True)

    class Meta:
        db_table="secondfile"





