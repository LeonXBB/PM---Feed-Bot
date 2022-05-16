from .coin_toss import coin_toss_popups
from .event import event_popups
from .period import period_popups
from .side_change import side_change_popups
from .technical_time_out import technical_time_out_popups
from .time_out import time_out_popups
from .commands import commands_popups

remainder_popups = [*coin_toss_popups, *event_popups, *period_popups, *side_change_popups, *technical_time_out_popups, *time_out_popups, *commands_popups]