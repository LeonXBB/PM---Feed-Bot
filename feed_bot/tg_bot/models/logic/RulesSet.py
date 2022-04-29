from django.db import models

from .LogicModel import LogicModel
from ..CharableListField import CharableListField

class RulesSet(LogicModel):
    
    name = models.CharField(max_length=5096, default="")

    win_event_by = models.IntegerField(default=0)
    win_period_by = CharableListField()

    periods_in_event = models.IntegerField(default=2)
    periods_to_win_event = models.IntegerField(default=2)

    points_in_period = CharableListField()
    points_to_win_period = CharableListField()

    stop_event_after_enough_periods = models.IntegerField(default=0)
    stop_period_after_enough_points = CharableListField()

    min_difference_periods_to_win_event = models.IntegerField(default=0)
    min_difference_points_to_win_period = CharableListField()

    points_per_period_per_score_per_team = CharableListField()
    scores_names = CharableListField()
    ball_control_after_score_per_score = CharableListField()
    pause_after_score_per_score = CharableListField()

    event_length_minutes = models.IntegerField(default=0)
    periods_lenght_minutes = CharableListField()

    interval_between_periods_munutes = CharableListField()

    event_timer_direction = models.IntegerField(default=0)
    period_timers_directions = CharableListField()
    event_timer_stops_at_pauses = models.IntegerField(default=0)
    period_timers_stop_at_pauses = CharableListField()

    side_changes_after_periods = CharableListField()
    side_changes_during_periods = CharableListField()
    side_changes_during_periods_scores = CharableListField()

    coin_tosses_before_periods = CharableListField()
    coin_toss_start_before_minutes  = CharableListField()

    time_outs_per_team_per_period = CharableListField()
    time_outs_lenghts_per_team_per_period = CharableListField()
    
    technical_time_outs_lenghts_per_period = CharableListField()
    technical_time_outs_at_score_per_period = CharableListField()
    
    actions_list = CharableListField()
    
    event_start_remainder_minutes_before = CharableListField()
    event_end_remainder_minutes_before = CharableListField()
    period_start_remainder_minutes_before = CharableListField()
    period_end_remainder_minutes_before = CharableListField()
    coin_toss_remainder_minutes_before = CharableListField()
