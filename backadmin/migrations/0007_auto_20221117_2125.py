# Generated by Django 3.1.7 on 2022-11-17 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backadmin', '0006_userinformation_ipconfig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinformation',
            name='stat',
            field=models.IntegerField(choices=[(0, '普通用户'), (1, '管理员'), (2, '超级管理员')], default=0),
        ),
    ]
