from django.db import models

from .LogicModel import LogicModel


class RulesSet(LogicModel):
    
    name = models.CharField(max_length=5096, default="")

    win_event_by = models.IntegerField(default=0)
    win_period_by = models.CharField(max_length=5096, default=';')

    periods_in_event = models.IntegerField(default=2)
    periods_to_win_event = models.IntegerField(default=2)

    points_in_period = models.IntegerField(default=2)
    points_to_win_period = models.CharField(max_length=5096, default=';')

    stop_event_after_enough_periods = models.BooleanField(default=False)
    stop_period_after_enough_points = models.CharField(max_length=5096, default=';')

    min_difference_periods_to_win_event = models.IntegerField(default=0)
    min_difference_points_to_win_period = models.CharField(max_length=5096, default=';')

    points_per_score_per_period = models.CharField(max_length=5096, default=';')
    scores_names = models.CharField(max_length=5096, default='()')

    event_length_minutes = models.IntegerField(default=0)
    periods_lenght_minutes = models.CharField(max_length=5096, default=';')

    interval_between_periods_munutes = models.CharField(max_length=5096, default=';')

    event_timer_direction = models.IntegerField(default=0) #######
    period_timers_directions = models.CharField(max_length=5096, default=';') #######

    timers_stop_at_pauses = models.IntegerField(default=0)

    side_changes_after_periods = models.CharField(max_length=5096, default=';')
    side_changes_during_periods = models.CharField(max_length=5096, default=';')
    side_changes_during_periods_scores = models.CharField(max_length=5096, default=';')

    coin_tosses_before_periods = models.CharField(max_length=5096, default='()')
    coin_toss_start_before_minutes  = models.CharField(max_length=5096, default=';')

    time_outs_per_team_per_period = models.CharField(max_length=5096, default='()')
    time_outs_lenghts_per_team_per_period = models.CharField(max_length=5096, default=';')
    
    technical_time_outs_lenghts_per_period = models.CharField(max_length=5096, default=';')
    technical_time_outs_at_score_per_period = models.CharField(max_length=5096, default=';')
    
    actions_list = models.CharField(max_length=5096, default='()')
    
    event_start_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    event_end_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    period_start_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    period_end_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    coin_toss_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    
    def register(self):
        pass

    def delete(self):
        pass