# Generated by Django 4.0.3 on 2022-03-25 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0003_scheduledmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledmessage',
            name='group_name',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AddField(
            model_name='scheduledmessage',
            name='is_active',
            field=models.IntegerField(default=1),
        ),
    ]
