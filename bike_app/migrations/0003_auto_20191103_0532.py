# Generated by Django 2.2.5 on 2019-11-03 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bike_app', '0002_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
    ]