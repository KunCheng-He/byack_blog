# Generated by Django 2.2.1 on 2019-06-12 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20190612_1256'),
    ]

    operations = [
        migrations.RenameField(
            model_name='readnum',
            old_name='readed_num',
            new_name='read_num',
        ),
    ]
