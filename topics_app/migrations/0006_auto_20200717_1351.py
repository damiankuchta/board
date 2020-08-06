# Generated by Django 3.0.6 on 2020-07-17 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topics_app', '0005_auto_20200710_0215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['creation_datetime']},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['last_post_datetime']},
        ),
        migrations.AddField(
            model_name='topic',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='topics_app.Topic'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='last_post_datetime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
