# Generated by Django 3.0.6 on 2020-07-17 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topics_app', '0006_auto_20200717_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='content',
        ),
    ]
