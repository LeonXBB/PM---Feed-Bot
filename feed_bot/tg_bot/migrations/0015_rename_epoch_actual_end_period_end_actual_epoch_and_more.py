# Generated by Django 4.0.3 on 2022-03-28 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0014_point_team_id_point_value'),
    ]

    operations = [
        migrations.RenameField(
            model_name='period',
            old_name='epoch_actual_end',
            new_name='end_actual_epoch',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='epoch_scheduled_end',
            new_name='end_scheduled_epoch',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='epoch_actual_start',
            new_name='start_actual_epoch',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='epoch_scheduled_start',
            new_name='start_scheduled_epoch',
        ),
    ]
