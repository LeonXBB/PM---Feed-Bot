# Generated by Django 4.0.3 on 2022-03-29 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0020_alter_rulesset_stop_period_after_enough_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='orgiginal_ball_possesion_team_id',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='period',
            name='original_left_team_id',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='period',
            name='original_right_team_id',
            field=models.IntegerField(default=-1),
        ),
    ]
