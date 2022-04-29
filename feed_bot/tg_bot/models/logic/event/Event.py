from decouple import config

from django.db import models

import time
import datetime

from ....bin.utils import Utils
from ....screens._utils.checks import check_time_outs
from ....screens.remainders.Remainder import Remainder

from ..LogicModel import LogicModel


class Event(LogicModel):  #TODO move template to different class?
    
    # statuses: 0 - being created, 1 - awaiting start, 2 - ongoing, 3 - between periods, 4 - finished
    
    active_status = models.IntegerField(default=1)

    admin_id = models.IntegerField(default=-1)

    competition_id = models.IntegerField(default=-1)
    rules_set_id = models.IntegerField(default=-1)

    date_scheduled =  models.CharField(max_length=5096, default="")
    time_scheduled = models.CharField(max_length=5096, default="")
   
    start_scheduled_epoch = models.CharField(max_length=5096, default="")
    start_actual_epoch = models.CharField(max_length=5096, default="")
    end_scheduled_epoch = models.CharField(max_length=5096, default="")
    end_actual_epoch = models.CharField(max_length=5096, default="")

    home_team_id = models.IntegerField(default=-1)
    away_team_id = models.IntegerField(default=-1)

    periods_ids = models.CharField(max_length=5096, default=";")

    coin_tosses_ids = models.CharField(max_length=5096, default=";")
    side_changes_ids = models.CharField(max_length=5096, default=";")

    # CREATE TEMPLATE 

    @classmethod
    def make_template(cls, user_id): #TODO JSON
        
        if len(res := cls._get_({"admin_id": user_id, "status": 0})) > 0:
            return res[0].id

        else:

            new_event = cls()
            new_event.admin_id = user_id
            new_event.status = 0
            new_event.save()

            Utils.api("event_template_created", "logic", event_id=new_event.id)

            return new_event.id

    def show_template(self): #TODO JSON

        from ..Team import Team
        from ..Competition import Competition
        from ..RulesSet import RulesSet

        from ...telebot.BotUser import BotUser

        home_team_name = "" if self.home_team_id == -1 else Team._get_({"id": self.home_team_id})[0].name 
        away_team_name = "" if self.away_team_id == -1 else Team._get_({"id": self.away_team_id})[0].name 
        
        competition_name = "" if self.competition_id == -1 else Competition._get_({"id": self.competition_id})[0].name  
        rules_set_name = "" if self.rules_set_id == -1 else RulesSet._get_({"id": self.rules_set_id})[0].name      

        formatters = (str(self.id), home_team_name, away_team_name, competition_name, rules_set_name, self.date_scheduled, self.time_scheduled)
        
        ready = True
        for x in formatters:
            if len(x) == 0:
                ready = False
                break

        if ready:
            return BotUser._get_({"id": self.admin_id})[0].show_screen_to("20", [formatters,])
        else:
            return BotUser._get_({"id": self.admin_id})[0].show_screen_to("21", [formatters,])

    def update_template(self, attr, val): #TODO JSON
        
        from .EventTemplateEdit import EventTemplateEdit

        new_edit = EventTemplateEdit()

        new_edit.event_id = self.id
        new_edit.field_name = attr
        new_edit.old_value = getattr(self, attr)
        new_edit.new_value = val

        created = eval(new_edit.created)
        created["at"] = str(int(time.time()))
        created["by"] = self.admin_id
        new_edit.created = dict(created)
        
        new_edit.save()

        setattr(self, attr, val) #TODO change so we don't actually save the values unless the user confirms the event, the show_template func should take its formatters values from the latest edits
        self.save()

        Utils.api("event_template_updated", "logic",
        event_id=self.id, attr="_".join(attr.split("_")[:-1]), old_val=new_edit.old_value, new_val=val)

    def cancel_edit_template(self): #TODO DO and JSON
        pass

    def save_template(self): #TODO JSON
               
        rv = self.start()

        return rv

    def cancel_save(self): #TODO DO and JSON
        pass

    # MATCH TEMPLATE

    def show_match_template(self, period_id):
       
        # (ball) team 1 (ball or '-') team 2 (ball)
        #
        # point_score 1 - point score 2 (total 1 - total 2)
        # (period score 1 - period score 2)
        #
        # time_outs: 1 - 2 (total 1 - total 2)
        # *action name 1* 1 - 2 (total 1 - total 2)
        # (*continue for all actions*)

        # ball control / pause / ball control
        # point 1 - point 2
        # (opt) time out 1 - time out 2
        # (opt) action 1 - action 2
        # (* continue for all actions *)

        from ..Team import Team
        from ..TimeOut import TimeOut
        from ..RulesSet import RulesSet
        from ..Period import Period
        from ..Point import Point
        from ..Action import Action

        from ...localization.TextString import TextString

        from ...telebot.BotUser import BotUser

        admin = BotUser._get_({"id": self.admin_id})[0]
        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        period_count = len(list((period_id for period_id in self.periods_ids.split(";") if period_id)))
        current_period = Period._get_({"id": period_id})[0]       

        rv = [] 
        formatters = []
        callbacks = []

        points_by_type_by_period = []
        sum_points_by_period = []
        periods_score = [0, 0]
        
        time_outs_all = []
        actions_all = []
        
        for action_type in rules_set.actions_list:
            if action_type:
                actions_all.append(list())

        for point_type in rules_set.scores_names:
            points_by_type_by_period.append(list())

        for period_id in self.periods_ids:
            if period_id:

                time_outs_all.append([0, 0])
                for action_type in actions_all:
                    action_type.append([0, 0])

                period = Period._get_({"id": int(period_id)})[0]

                sum_points_by_period.append([0, 0])

                for i, point_type in enumerate(rules_set.scores_names):
                    points_by_type_by_period[i].append([0, 0])

                    for point_id in period.points_ids.split(";"):
                        if point_id:
                            point = Point._get_({"id": int(point_id)})[0]
                            if point.type == i:
                                if point.team_id == current_period.left_team_id:
                                    points_by_type_by_period[i][-1][0] += point.value
                                    sum_points_by_period[-1][0] += point.value
                                    points_by_type_by_period[i][-1][1] += point.opposite_value
                                    sum_points_by_period[-1][1] += point.opposite_value
                                else:
                                    points_by_type_by_period[i][-1][1] += point.value
                                    sum_points_by_period[-1][1] += point.value
                                    points_by_type_by_period[i][-1][0] += point.opposite_value
                                    sum_points_by_period[-1][0] += point.opposite_value

                if period.status == 2:
                    if sum_points_by_period[-1][0] > sum_points_by_period[-1][1]:
                        periods_score[0] += 1
                    elif sum_points_by_period[-1][0] < sum_points_by_period[-1][1]:
                        periods_score[1] += 1

                for time_out_id in period.timeouts_ids.split(";"):
                    if time_out_id:
                        time_out = TimeOut._get_({"id": int(time_out_id)})[0]
                        if time_out.team_id == current_period.left_team_id:
                            time_outs_all[-1][0] += 1
                        elif time_out.team_id == current_period.right_team_id:
                            time_outs_all[-1][1] += 1

                for action_id in period.actions_ids.split(";"):
                    if action_id:
                        action = Action._get_({"id": int(action_id)})[0]
                        if action.team_id == current_period.left_team_id:
                            actions_all[action.type_id][-1][0] += 1
                        else:
                            actions_all[action.type_id][-1][1] += 1

        ball = getattr(TextString._get_({"screen_id": "active", "position_index": 0})[0], f"language_{admin.language_id + 1}")
        left_ball = ball if current_period.ball_possesion_team_id == current_period.left_team_id else ""
        central_ball = ball if current_period.ball_possesion_team_id != current_period.left_team_id and current_period.ball_possesion_team_id != current_period.right_team_id else " --- "
        right_ball = ball if current_period.ball_possesion_team_id == current_period.right_team_id else ""

        left_team_name = Team._get_({"id": current_period.left_team_id})[0].name
        right_team_name = Team._get_({"id": current_period.right_team_id})[0].name

        header = f"{left_ball}{left_team_name}{central_ball}{right_team_name}{right_ball}"
                      
        scores = ""        
        
        scores += f"{sum_points_by_period[-1][0]} - {sum_points_by_period[-1][1]}"
        scores += f"\n({periods_score[0]} - {periods_score[1]})\n"

        for i, point_type in enumerate(rules_set.scores_names):
                
            sum_0 = sum_1 = 0
            for period_ in points_by_type_by_period[i]:
                sum_0 += period_[0]
                sum_1 += period_[1]

            try:
                scores += f"\n   {point_type}: {points_by_type_by_period[i][-1][0]} - {points_by_type_by_period[i][-1][1]} ({sum_0} - {sum_1})"
            except: #for when we didnt have any points of this type (e.g. when we have only one period) #TODO: find a better way to do this
                    pass 

        time_out_string = "\n"
        if check_time_outs(0, self.id) != 0 or check_time_outs(1, self.id) != 0:
            time_out_word = getattr(TextString._get_({"screen_id": "active", "position_index": 1})[0], f"language_{admin.language_id + 1}")
            
            try: # if we have time outs #TODO find a better way to do this (check lenght)
                time_outs_1 = time_outs_all[-1][0]
            except: # if we dont have time outs
                time_outs_1 = 0

            try:
                time_outs_2 = time_outs_all[-1][1]
            except:
                time_outs_2 = 0

            time_outs_1_total = 0
            time_outs_2_total = 0

            for period in time_outs_all:
                try:
                    time_outs_1_total += period[0]
                except:
                    pass

                try:
                    time_outs_2_total += period[1]
                except:
                    pass

            time_out_string = f"\n\n{time_out_word}: {time_outs_1} - {time_outs_2} ({time_outs_1_total} - {time_outs_2_total})"

        bottom_string = f"{time_out_string}\n"

        for i, action in enumerate(rules_set.actions_list):
            if action:
                try: # if we have actions #TODO find a better way to do this (check lenght)
                    action_1 = actions_all[i][-1][0]
                except: # if we dont have actions
                    action_1 = 0

                try:
                    action_2 = actions_all[i][-1][1]
                except:
                    action_2 = 0

                action_1_total = 0
                action_2_total = 0

                try: # if we have actions #TODO find a better way to do this (check lenght)
                    for period in actions_all[i]:

                        try: 
                            action_1_total += period[0]
                        except:
                            pass
                        
                        try:
                            action_2_total += period[1]
                        except:
                            pass
                except: # if we dont have actions
                    pass

                action_string = f"\n   {action}: {action_1} - {action_2} ({action_1_total} - {action_2_total})"

                bottom_string += f"{action_string}"

        formatters.append([header, scores, bottom_string])

        callbacks.append(list())
        for i in range(20): # TODO calculate excat number of buttons!!!
            callbacks[-1].append(current_period.id)

        rv.append(admin.show_screen_to('30', formatters, callbacks))

        rv.append(["ignore", 30])

        return rv

    def show_paused_match_template(self, period_id):
        
        from ..Team import Team
        from ..TimeOut import TimeOut
        from ..RulesSet import RulesSet
        from ..Period import Period
        from ..Point import Point
        from ..Action import Action

        from ...localization.TextString import TextString

        from ...telebot.BotUser import BotUser

        admin = BotUser._get_({"id": self.admin_id})[0]
        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        period_count = len(list((period_id for period_id in self.periods_ids.split(";") if period_id)))
        current_period = Period._get_({"id": period_id})[0]       

        rv = [] 
        formatters = []
        callbacks = []

        points_by_type_by_period = []
        sum_points_by_period = []
        periods_score = [0, 0]
        
        time_outs_all = []
        actions_all = []
        
        for action_type in rules_set.actions_list:
            actions_all.append(list())

        for point_type in rules_set.scores_names:
            points_by_type_by_period.append(list())

        for period_id in self.periods_ids.split(";"):
            if period_id:

                time_outs_all.append([0, 0])
                for action_type in actions_all:
                    action_type.append([0, 0])

                period = Period._get_({"id": int(period_id)})[0]

                sum_points_by_period.append([0, 0])

                for i, point_type in enumerate(rules_set.scores_names):
                    points_by_type_by_period[i].append([0, 0])

                    for point_id in period.points_ids.split(";"):
                        if point_id:
                            point = Point._get_({"id": int(point_id)})[0]
                            if point.type == i:
                                if point.team_id == current_period.left_team_id:
                                    points_by_type_by_period[i][-1][0] += point.value
                                    sum_points_by_period[-1][0] += point.value
                                    points_by_type_by_period[i][-1][1] += point.opposite_value
                                    sum_points_by_period[-1][1] += point.opposite_value
                                else:
                                    points_by_type_by_period[i][-1][1] += point.value
                                    sum_points_by_period[-1][1] += point.value
                                    points_by_type_by_period[i][-1][0] += point.opposite_value
                                    sum_points_by_period[-1][0] += point.opposite_value

                if period.status == 2:
                    if sum_points_by_period[-1][0] > sum_points_by_period[-1][1]:
                        periods_score[0] += 1
                    elif sum_points_by_period[-1][0] < sum_points_by_period[-1][1]:
                        periods_score[1] += 1

                for time_out_id in period.timeouts_ids.split(";"):
                    if time_out_id:
                        time_out = TimeOut._get_({"id": int(time_out_id)})[0]
                        if time_out.team_id == current_period.left_team_id:
                            time_outs_all[-1][0] += 1
                        elif time_out.team_id == current_period.right_team_id:
                            time_outs_all[-1][1] += 1

                for action_id in period.actions_ids.split(";"):
                    if action_id:
                        action = Action._get_({"id": int(action_id)})[0]
                        if action.team_id == current_period.left_team_id:
                            actions_all[action.type_id][-1][0] += 1
                        else:
                            actions_all[action.type_id][-1][1] += 1

        ball = getattr(TextString._get_({"screen_id": "active", "position_index": 0})[0], f"language_{admin.language_id + 1}")
        left_ball = ball if current_period.ball_possesion_team_id == current_period.left_team_id else ""
        central_ball = ball if current_period.ball_possesion_team_id != current_period.left_team_id and current_period.ball_possesion_team_id != current_period.right_team_id else " --- "
        right_ball = ball if current_period.ball_possesion_team_id == current_period.right_team_id else ""

        left_team_name = Team._get_({"id": current_period.left_team_id})[0].name
        right_team_name = Team._get_({"id": current_period.right_team_id})[0].name

        header = f"{left_ball}{left_team_name}{central_ball}{right_team_name}{right_ball}"
                      
        scores = ""        
        
        scores += f"{sum_points_by_period[-1][0]} - {sum_points_by_period[-1][1]}"
        scores += f"\n({periods_score[0]} - {periods_score[1]})\n"

        for i, point_type in enumerate(rules_set.scores_names):
                
            sum_0 = sum_1 = 0
            for period_ in points_by_type_by_period[i]:
                sum_0 += period_[0]
                sum_1 += period_[1]

            try:
                scores += f"\n   {point_type}: {points_by_type_by_period[i][-1][0]} - {points_by_type_by_period[i][-1][1]} ({sum_0} - {sum_1})"
            except: #for when we didnt have any points of this type (e.g. when we have only one period) #TODO: find a better way to do this
                pass 

        time_out_string = "\n"
        if check_time_outs(0, self.id) != 0 or check_time_outs(1, self.id) != 0:
            time_out_word = getattr(TextString._get_({"screen_id": "active", "position_index": 1})[0], f"language_{admin.language_id + 1}")
            
            try: # if we have time outs #TODO find a better way to do this (check lenght)
                time_outs_1 = time_outs_all[-1][0]
            except: # if we dont have time outs
                time_outs_1 = 0

            try:
                time_outs_2 = time_outs_all[-1][1]
            except:
                time_outs_2 = 0

            time_outs_1_total = 0
            time_outs_2_total = 0

            for period in time_outs_all:
                try:
                    time_outs_1_total += period[0]
                except:
                    pass

                try:
                    time_outs_2_total += period[1]
                except:
                    pass

            time_out_string = f"\n\n{time_out_word}: {time_outs_1} - {time_outs_2} ({time_outs_1_total} - {time_outs_2_total})"

        bottom_string = f"{time_out_string}\n"

        for i, action in enumerate(rules_set.actions_list):
            if action:
                try: # if we have actions #TODO find a better way to do this (check lenght)
                    action_1 = actions_all[i][-1][0]
                except: # if we dont have actions
                    action_1 = 0

                try:
                    action_2 = actions_all[i][-1][1]
                except:
                    action_2 = 0

                action_1_total = 0
                action_2_total = 0

                try: # if we have actions #TODO find a better way to do this (check lenght)
                    for period in actions_all[i]:

                        try: 
                            action_1_total += period[0]
                        except:
                            pass
                        
                        try:
                            action_2_total += period[1]
                        except:
                            pass
                except: # if we dont have actions
                    pass

                action_string = f"\n   {action}: {action_1} - {action_2} ({action_1_total} - {action_2_total})"

                bottom_string += f"{action_string}"

        formatters.append([header, scores, bottom_string])

        callbacks.append(list())
        for i in range(3):
            callbacks[-1].append(current_period.id)

        rv.append(admin.show_screen_to('31', formatters, callbacks))

        rv.append(["ignore", 31])

        return rv #TODO either change or unite with the one above

    # LOGIC

    def start(self): #TODO JSON
        
        from ..RulesSet import RulesSet

        from ...telebot.BotUser import BotUser

        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        admin = BotUser._get_({"id": self.admin_id})[0]

        self.status = 1

        day, month, year = self.date_scheduled.split("-")
        hour, minute = self.time_scheduled.split(":")

        self.start_scheduled_epoch = str(int(datetime.datetime(int(year), int(month), int(day), int(hour), int(minute)).timestamp())).split(".")[0] 

        if rules_set.event_length_minutes == 0:
            self.end_scheduled_epoch= "0"
        else:
   
            end_time = str(int(self.start_scheduled_epoch) + int(rules_set.event_length_minutes) * 60)
            self.end_scheduled_epoch = end_time

        self.save()
        
        Utils.api("event_scheduled", "logic", event_id=self.id, event_epoch=int(self.start_scheduled_epoch))

        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *self.run()]

        return rv

    def end(self): #TODO JSON

        from ..Team import Team
        
        from ...telebot.BotUser import BotUser

        self.status = 4
        self.end_actual_epoch = int(time.time())
        self.save()
        
        admin = BotUser._get_({"id": self.admin_id})[0]

        home_team_name = Team._get_({"id": self.home_team_id})[0].name
        away_team_name = Team._get_({"id": self.away_team_id})[0].name

        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *Remainder._get_("EventEnded").schedule(int(time.time()), admin.id, [[self.id, home_team_name, away_team_name], ], f"event_{self.id}_ended", [[self.id, ], ])]

        Utils.api("event_ended", "logic", event_id=self.id)

        return  rv #TODO static formatter 

    def run(self, command="_"): #TODO JSON
        
        from ..RulesSet import RulesSet
        from ..Team import Team
        from ..CoinToss import CoinToss
        from ..Period import Period
        from ..Point import Point
        from ..SideChange import SideChange

        from ...telebot.BotUser import BotUser
        from ...telebot.ScheduledMessage import ScheduledMessage

        rv = []

        admin = BotUser._get_({"id": self.admin_id})[0]

        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        home_team_name = Team._get_({"id": self.home_team_id})[0].name
        away_team_name = Team._get_({"id": self.away_team_id})[0].name

        period_count = len(Period.objects.filter(event_id=self.id))
        coin_toss_count = len(CoinToss.objects.filter(event_id=self.id))
        
        try: # TODO change to check if we have a period
            last_period_id = Period._get_({"event_id": self.id})[-1].id
        except:
            pass

        point_score = []

        for period_id in self.periods_ids.split(";"):
            if period_id:
                period = Period._get_({"id": int(period_id)})[0]
                point_score.append([0, 0])

                for point_id in period.points_ids.split(";"):
                    if point_id:
                        point = Point._get_({"id": int(point_id)})[0]                           
                        point_score[-1][0 if point.team_id == self.home_team_id else 1] += point.value
                        point_score[-1][0 if point.team_id != self.home_team_id else 1] += point.opposite_value

            int_score = [0, 0] #TODO rename

            for sublist in point_score:
                if sublist[0] > sublist[1]:
                    int_score[0] += 1
                elif sublist[0] < sublist[1]:
                    int_score[1] += 1

            score_sum = [0, 0]

            for sublist in point_score:
                score_sum[0] += sublist[0]
                score_sum[1] += sublist[1]

        def check_remainders():

            def check_sent_already(remainder_id, group_name): #TODO JSON move to utils
                return len(ScheduledMessage._get_({"content_id": remainder_id, "group_name": group_name})) > 0
            
            if self.status == 1 and not check_sent_already(104, f"event_{self.id}_start"):   
                rv.extend(Remainder._get_("EventScheduled").schedule(int(time.time()), self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            #check coin_toss
            if self.status != 4 and (period_count < rules_set.periods_in_event or rules_set.periods_in_event == 0) and rules_set.coin_tosses_before_periods[period_count] == 1: # as of 1st run we haven't created period obj yet
                
                if not check_sent_already(140, f"event_{self.id}_coin_toss_{coin_toss_count}"):

                    when = int(self.start_scheduled_epoch) - int(rules_set.coin_toss_start_before_minutes[coin_toss_count]) * 60
                    
                    rv.extend(Remainder._get_("CoinTossHappens").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_coin_toss_{coin_toss_count}", [[self.id, self.id], ]))

                    for offset in rules_set.coin_toss_remainder_minutes_before[coin_toss_count - 1]:
                        if offset:
                            rv.extend(Remainder._get_("CoinTossAboutToHappen").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_coin_toss_{coin_toss_count}", [[self.id, self.id], ]))
            

                    Utils.api("coin_toss_scheduled", "logic", event_id=self.id, coin_toss_count=coin_toss_count, period_count=period_count, coin_toss_epoch=when)
            # check event start
            
            if self.status == 1 and not check_sent_already(100, f"event_{self.id}_start") and (period_count < rules_set.periods_in_event or rules_set.periods_in_event == 0) and not rules_set.coin_tosses_before_periods[period_count] == 1:
                    
                when = int(self.start_scheduled_epoch)

                rv.extend(Remainder._get_("EventStart").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_start", [[self.id, self.id], ]))
    
                for offset in rules_set.event_start_remainder_minutes_before:
                    if offset:
                        rv.extend(Remainder._get_("EventAboutToStart").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            # check event end

            if rules_set.event_length_minutes != 0 and self.status == 2 and not check_sent_already(101, f"event_{self.id}_end"):
                    
                when = int(self.end_scheduled_epoch)
                
                rv.extend(Remainder._get_("EventEnd").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_end", [[self.id, self.id], ]))
    
                for offset in rules_set.event_end_remainder_minutes_before:
                    if offset:
                        rv.extend(Remainder._get_("EventAboutToEnd").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            # check side change reminders
            # if it's between periods and it's time to change sides and not sent yet
            if self.status == 3 and (period_count < rules_set.periods_in_event or rules_set.periods_in_event == 0) and rules_set.side_changes_after_periods[period_count - 1] == 1 and not check_sent_already(150, f"event_{self.id}_side_change_after_period_{period_count}"):
                rv.extend((Remainder._get_("SideChangeHappens").schedule(int(time.time()), self.admin_id, [[] ,], f"event_{self.id}_side_change_after_period_{period_count}", [[], ])))
            
        def check_coin_toss():
            return data[0] == "coinToss"

        def check_end():

            def check_end_by_score_period():

                return rules_set.win_event_by == 2 and (((max(int_score) >= rules_set.periods_to_win_event and (rules_set.stop_event_after_enough_periods == 1)) or (max(int_score) >= rules_set.periods_in_event or rules_set.periods_in_event == 0)) and max(int_score) - min(int_score) > rules_set.min_difference_periods_to_win_event)

            def check_end_by_score_sum():
                return rules_set.win_event_by == 3 and (((max(score_sum) >= rules_set.periods_to_win_event and rules_set.stop_event_after_enough_periods == 1) or( max(score_sum) > rules_set.periods_in_event) or rules_set.periods_in_event == 0) and max(score_sum) - min(score_sum) > rules_set.min_difference_periods_to_win_event)

            return check_end_by_score_period() or check_end_by_score_sum()

        def check_side_change():
            try: #TODO check lenght instead of try
                return self.status == 3 and rules_set.side_changes_after_periods[period_count - 1] == 1
            except:
                return False

        def check_new_period():
            for period_id in self.periods_ids.split(";"):
                if period_id:
                    period = Period._get_({"id": int(period_id)})[0]

            return self.status == 3 and not rules_set.coin_tosses_before_periods[period_count] == 1 and not period.status == 0

        data = command.split("_")

        check_remainders()

        if check_end():
            return self.end()

        if check_new_period() and not check_coin_toss(): #TODO fix for 5th set

            new_period = Period()
            new_period.event_id = self.id
            new_period.save()

            rv.extend(new_period.start())

            new_period.save()

        if check_side_change():
            
            side_change_ = SideChange()

            side_change_.happen(self.id, -1, f"{int_score[0]}:{int_score[1]}")
            side_change_.save()

            Utils.api("side_change_after_period_happened", "logic", event_id=self.id, period_count=period_count, period_id=last_period_id, side_change_id=side_change_.id)

        if check_coin_toss():
            
            obj = CoinToss()

            obj.happen(self.id, int(self.start_scheduled_epoch) - int(rules_set.coin_toss_start_before_minutes[coin_toss_count]) * 60, period_count+1, self.home_team_id)
            obj.save()

            self.coin_tosses_ids += f"{obj.id};"
            self.save()

            Utils.api("coin_toss_started", "logic", event_id=self.id, coin_toss_id=obj.id, coin_toss_count=coin_toss_count, period_count=period_count) #TODO move to when the user sends a button

            rv.extend(obj.show_template())
        
        return rv

    def cancel(self, task): #TODO JSON

        from ...telebot.BotUser import BotUser

        def cancel_event():
            
            self.active_status = 0
            self.save()

            Utils.api("event_cancelled", "logic", event_id=self.id) #TODO add event template somewhere in here (move from 'clear' button)

            return BotUser._get_({"id": self.admin_id})[0].show_list_of_events(True)

        def cancel_cancel_event():
            self.active_status = 1
            self.save()
            return BotUser._get_({"id": self.admin_id})[0].show_list_of_events(True)

        def cancel_run():
            pass

        def cancel_start():
            pass

        def cancel_end():
            pass

        return eval(f"cancel_{task}()")