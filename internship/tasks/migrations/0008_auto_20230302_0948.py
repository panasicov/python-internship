# Generated by Django 3.2.16 on 2023-03-02 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_remove_timelog_stop'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('id',), 'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
        migrations.AlterModelOptions(
            name='timelog',
            options={'ordering': ('id',), 'verbose_name': 'TimeLog', 'verbose_name_plural': 'TimeLogs'},
        ),
    ]
