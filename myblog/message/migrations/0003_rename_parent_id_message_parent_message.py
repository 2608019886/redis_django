# Generated by Django 3.2.8 on 2021-11-01 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0002_rename_parent_message_message_parent_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='parent_id',
            new_name='parent_message',
        ),
    ]