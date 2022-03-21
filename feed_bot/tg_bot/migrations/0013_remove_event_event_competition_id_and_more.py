# Generated by Django 4.0.3 on 2022-03-20 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0012_competition_remove_event_competition_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_competition_id',
        ),
        migrations.AddField(
            model_name='event',
            name='competition_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='admin_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='away_team_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='epoch_actual',
            field=models.CharField(default='', max_length=5096),
        ),
        migrations.AlterField(
            model_name='event',
            name='epoch_scheduled',
            field=models.CharField(default='', max_length=5096),
        ),
        migrations.AlterField(
            model_name='event',
            name='home_team_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='rules_set_id',
            field=models.IntegerField(default=0),
        ),
    ]
