# Generated by Django 3.0.6 on 2020-07-10 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards_app', '0011_auto_20200630_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='add_new_posts_restictions',
            field=models.IntegerField(choices=[(5, 'All'), (4, 'Registered'), (3, 'Selected Groups'), (2, 'Admins'), (1, 'Superusers'), (0, 'None')], default=4, help_text='Lowest user group to be able to add new posts', max_length=124),
        ),
        migrations.AlterField(
            model_name='board',
            name='add_new_topics_restrictions',
            field=models.IntegerField(choices=[(5, 'All'), (4, 'Registered'), (3, 'Selected Groups'), (2, 'Admins'), (1, 'Superusers'), (0, 'None')], default=4, help_text='Lowest user group to be able to add new topics', max_length=124),
        ),
        migrations.AlterField(
            model_name='board',
            name='visibility',
            field=models.IntegerField(choices=[(5, 'All'), (4, 'Registered'), (3, 'Selected Groups'), (2, 'Admins'), (1, 'Superusers'), (0, 'None')], default=5, help_text='Lowest user group to be able to see Group/Board', max_length=124),
        ),
        migrations.AlterField(
            model_name='boardgroup',
            name='add_new_posts_restictions',
            field=models.IntegerField(choices=[(5, 'All'), (4, 'Registered'), (3, 'Selected Groups'), (2, 'Admins'), (1, 'Superusers'), (0, 'None')], default=4, help_text='Lowest user group to be able to add new posts', max_length=124),
        ),
        migrations.AlterField(
            model_name='boardgroup',
            name='add_new_topics_restrictions',
            field=models.IntegerField(choices=[(5, 'All'), (4, 'Registered'), (3, 'Selected Groups'), (2, 'Admins'), (1, 'Superusers'), (0, 'None')], default=4, help_text='Lowest user group to be able to add new topics', max_length=124),
        ),
        migrations.AlterField(
            model_name='boardgroup',
            name='visibility',
            field=models.IntegerField(choices=[(5, 'All'), (4, 'Registered'), (3, 'Selected Groups'), (2, 'Admins'), (1, 'Superusers'), (0, 'None')], default=5, help_text='Lowest user group to be able to see Group/Board', max_length=124),
        ),
    ]
