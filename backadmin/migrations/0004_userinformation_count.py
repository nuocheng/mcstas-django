# Generated by Django 3.1.7 on 2022-11-16 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backadmin', '0003_auto_20221107_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinformation',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]