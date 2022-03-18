from .active_event import active_event_screens
from .authorization import authorization_screens 
from .main_menu import main_menu_screens
from .event_list import event_list_screens
from .new_event import new_event_screens
from .rule_sets_edit import rule_set_edit_screens

from .remainders import remainder_popups

all_screens = [*active_event_screens, *authorization_screens, *main_menu_screens, *event_list_screens, *new_event_screens, *rule_set_edit_screens, *remainder_popups]