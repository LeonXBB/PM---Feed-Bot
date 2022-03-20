# Generated by Django 4.0.3 on 2022-03-20 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0009_alter_event_created_alter_rulesset_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='created',
        ),
        migrations.RemoveField(
            model_name='rulesset',
            name='created',
        ),
        migrations.RemoveField(
            model_name='team',
            name='created',
        ),
        migrations.AddField(
            model_name='rulesset',
            name='competition_name',
            field=models.CharField(default=';', max_length=512),
        ),
        migrations.AddField(
            model_name='team',
            name='competition_name',
            field=models.CharField(default=';', max_length=512),
        ),
        migrations.AlterField(
            model_name='event',
            name='competition_name',
            field=models.CharField(default='', max_length=512),
        ),
    ]
