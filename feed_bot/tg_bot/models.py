from decouple import config

from django.db import models

import hashlib
import time
import datetime

from .bin.utils import Utils

from .screens.Screen import Screen
from .screens.remainders.Remainder import Remainder

from .screens._utils.checks import check_time_outs

#LOGIC #TODO sepatate by different files

class LogicModel(models.Model):
    
    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    created = models.CharField(max_length=5096, default=f"{{}}") # "by": user_id, "at": timestamp
    status = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def _cancel_(self):
        self.status = 5

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

    def make_template(self): #TODO DO and JSON
        pass

    def show_template(self): #TODO JSON

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

        Utils.api("new_event_template_value_update", "logic",
        event_id=self.id, attr=attr, val=val)

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
        
        for action_type in eval(rules_set.actions_list):
            if action_type:
                actions_all.append(list())

        for point_type in eval(rules_set.scores_names):
            points_by_type_by_period.append(list())

        for period_id in self.periods_ids.split(";"):
            if period_id:

                time_outs_all.append([0, 0])
                for action_type in actions_all:
                    action_type.append([0, 0])

                period = Period._get_({"id": int(period_id)})[0]

                sum_points_by_period.append([0, 0])

                for i, point_type in enumerate(eval(rules_set.scores_names)):
                    points_by_type_by_period[i].append([0, 0])

                    for point_id in period.points_ids.split(";"):
                        if point_id:
                            point = Point._get_({"id": int(point_id)})[0]
                            if point.type == i:
                                if point.team_id == current_period.left_team_id:
                                    points_by_type_by_period[i][-1][0] += point.value
                                    sum_points_by_period[-1][0] += point.value
                                else:
                                    points_by_type_by_period[i][-1][1] += point.value
                                    sum_points_by_period[-1][1] += point.value

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

        for i, point_type in enumerate(eval(rules_set.scores_names)):
                
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

        for i, action in enumerate(eval(rules_set.actions_list)):
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
        
        for action_type in eval(rules_set.actions_list):
            actions_all.append(list())

        for point_type in eval(rules_set.scores_names):
            points_by_type_by_period.append(list())

        for period_id in self.periods_ids.split(";"):
            if period_id:

                time_outs_all.append([0, 0])
                for action_type in actions_all:
                    action_type.append([0, 0])

                period = Period._get_({"id": int(period_id)})[0]

                sum_points_by_period.append([0, 0])

                for i, point_type in enumerate(eval(rules_set.scores_names)):
                    points_by_type_by_period[i].append([0, 0])

                    for point_id in period.points_ids.split(";"):
                        if point_id:
                            point = Point._get_({"id": int(point_id)})[0]
                            if point.type == i:
                                if point.team_id == current_period.left_team_id:
                                    points_by_type_by_period[i][-1][0] += point.value
                                    sum_points_by_period[-1][0] += point.value
                                else:
                                    points_by_type_by_period[i][-1][1] += point.value
                                    sum_points_by_period[-1][1] += point.value

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

        for i, point_type in enumerate(eval(rules_set.scores_names)):
                
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

        for i, action in enumerate(eval(rules_set.actions_list)):
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
        
        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *self.run()]

        return rv

    def end(self): #TODO JSON
        
        self.status = 4
        self.end_actual_epoch = int(time.time())
        self.save()
        
        admin = BotUser._get_({"id": self.admin_id})[0]

        home_team_name = Team._get_({"id": self.home_team_id})[0].name
        away_team_name = Team._get_({"id": self.away_team_id})[0].name

        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *Remainder._get_("EventEnded").schedule(int(time.time()), admin.id, [[self.id, home_team_name, away_team_name], ], f"event_{self.id}_ended", [[self.id, ], ])]

        return  rv #TODO static formatter 

    def run(self, command="_"): #TODO JSON
        
        rv = []

        admin = BotUser._get_({"id": self.admin_id})[0]

        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        home_team_name = Team._get_({"id": self.home_team_id})[0].name
        away_team_name = Team._get_({"id": self.away_team_id})[0].name

        period_count = len(Period.objects.filter(event_id=self.id))
        coin_toss_count = len(CoinToss.objects.filter(event_id=self.id))
        
        point_score = []

        for period_id in self.periods_ids.split(";"):
            if period_id:
                period = Period._get_({"id": int(period_id)})[0]
                point_score.append([0, 0])

                for point_id in period.points_ids.split(";"):
                    if point_id:
                        point = Point._get_({"id": int(point_id)})[0]                           
                        point_score[-1][0 if point.team_id == self.home_team_id else 1] += point.value

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
            if self.status != 4 and period_count < rules_set.periods_in_event and eval(rules_set.coin_tosses_before_periods)[period_count - 1] == "1":
                
                if not check_sent_already(140, f"event_{self.id}_coin_toss_{period_count}"):

                    when = int(self.start_scheduled_epoch) - int(rules_set.coin_toss_start_before_minutes.split(";")[coin_toss_count]) * 60
                    
                    rv.extend(Remainder._get_("CoinTossHappens").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_coin_toss_{period_count}", [[self.id, self.id], ]))

                    for offset in rules_set.coin_toss_remainder_minutes_before.split(";")[coin_toss_count - 1].split(","):
                        if offset:
                            rv.extend(Remainder._get_("CoinTossAboutToHappen").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_coin_toss_{period_count}", [[self.id, self.id], ]))
            
            # check event start
            
            if self.status == 1 and not check_sent_already(100, f"event_{self.id}_start") and period_count < rules_set.periods_in_event and not eval(rules_set.coin_tosses_before_periods)[period_count - 1] == "1":
                    
                when = int(self.start_scheduled_epoch)

                rv.extend(Remainder._get_("EventStart").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_start", [[self.id, self.id], ]))
    
                for offset in rules_set.event_start_remainder_minutes_before.split(";"):
                    if offset:
                        rv.extend(Remainder._get_("EventAboutToStart").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            # check event end

            if rules_set.event_length_minutes != 0 and self.status == 2 and not check_sent_already(101, f"event_{self.id}_end"):
                    
                when = int(self.end_scheduled_epoch)
                
                rv.extend(Remainder._get_("EventEnd").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_end", [[self.id, self.id], ]))
    
                for offset in rules_set.event_end_remainder_minutes_before.split(";"):
                    if offset:
                        rv.extend(Remainder._get_("EventAboutToEnd").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            # check side change reminders
            # if it's between periods and it's time to change sides and not sent yet
            if self.status == 3 and period_count < rules_set.periods_in_event and rules_set.side_changes_after_periods.split(';')[period_count - 1] == "1" and not check_sent_already(150, f"event_{self.id}_side_change_after_period_{period_count}"):
                rv.extend((Remainder._get_("SideChangeHappens").schedule(int(time.time()), self.admin_id, [[] ,], f"event_{self.id}_side_change_after_period_{period_count}", [[], ])))
            
        def check_coin_toss():
            return data[0] == "coinToss"

        def check_end():

            def check_end_by_score_period():

                print(rules_set.win_event_by, 2)
                print()

                return rules_set.win_event_by == 2 and (((max(int_score) >= rules_set.periods_to_win_event and ((rules_set.stop_event_after_enough_periods == 1) or (rules_set.stop_event_after_enough_periods == True))) or max(int_score) >= rules_set.periods_in_event) and max(int_score) - min(int_score) > rules_set.min_difference_periods_to_win_event)

            def check_end_by_score_sum():
                return rules_set.win_event_by == 3 and (((max(score_sum) >= rules_set.periods_to_win_event and rules_set.stop_event_after_enough_periods == 1) or max(score_sum) > rules_set.periods_in_event) and max(score_sum) - min(score_sum) > rules_set.min_difference_periods_to_win_event)

            return check_end_by_score_period() or check_end_by_score_sum()

        def check_side_change():
            try: #TODO check lenght instead of try
                return self.status == 3 and rules_set.side_changes_after_periods.split(';')[period_count - 1] == "1"
            except:
                return False

        def check_new_period():
            for period_id in self.periods_ids.split(";"):
                if period_id:
                    period = Period._get_({"id": int(period_id)})[0]

            return self.status == 3 and not eval(rules_set.coin_tosses_before_periods)[period_count - 1] == "1" and not period.status == 0

        data = command.split("_")

        check_remainders()

        if check_end():
            return self.end()

        if check_new_period() and not check_coin_toss(): #TODO fix for 5th set

            new_period = Period()
            new_period.event_id = self.id
            new_period.save()

            rv.extend(new_period.start())

        if check_side_change():
            
            obj = SideChange()

            obj.happen(self.id, -1, f"{int_score[0]}:{int_score[1]}")
            obj.save()

        if check_coin_toss():
            
            obj = CoinToss()

            obj.happen(self.id, int(self.start_scheduled_epoch) - int(rules_set.coin_toss_start_before_minutes.split(";")[coin_toss_count]) * 60, period_count+1, self.home_team_id)
            obj.save()

            self.coin_tosses_ids += f"{obj.id};"
            self.save()

            rv.extend(obj.show_template())
        
        return rv

    def cancel(self, task): #TODO JSON

        def cancel_event():
            self.active_status = 0
            self.save()
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

class EventTemplateEdit(LogicModel): #TODO move template to different class and change all references to it

    event_id = models.IntegerField(default=-1)
    field_name = models.CharField(max_length=5096)
    old_value = models.CharField(max_length=5096)
    new_value = models.CharField(max_length=5096)

    def undo(seld):
        pass

class Period(LogicModel):

    # statuses 0 - awaiting_start, 1 - ongoing, 2 - finished

    event_id = models.IntegerField(default=-1)

    start_scheduled_epoch = models.CharField(max_length=5096, default="")
    end_scheduled_epoch = models.CharField(max_length=5096, default="")
    start_actual_epoch = models.CharField(max_length=5096, default="")
    end_actual_epoch = models.CharField(max_length=5096, default="")

    left_team_id = models.IntegerField(default=-1)
    right_team_id = models.IntegerField(default=-1)
    ball_possesion_team_id = models.IntegerField(default=-1)

    original_left_team_id = models.IntegerField(default=-1)
    original_right_team_id = models.IntegerField(default=-1)
    original_ball_possesion_team_id = models.IntegerField(default=-1)

    is_paused = models.IntegerField(default=0)

    timeouts_ids = models.CharField(max_length=5096, default=";")
    points_ids = models.CharField(max_length=5096, default=";")
    actions_ids = models.CharField(max_length=5096, default=";")
    side_changes_ids = models.CharField(max_length=5096, default=";")

    def start(self): #TODO JSON
        
        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        admin = BotUser._get_({"id": event.admin_id})[0]
       
        periods_count = len(Period._get_({"event_id": self.event_id}))
        
        if periods_count == 1:
            # 1st event
            self.start_scheduled_epoch = event.start_scheduled_epoch

            if self.left_team_id == -1 or self.right_team_id == -1 or self.ball_possesion_team_id == -1:
                self.left_team_id = event.home_team_id
                self.right_team_id = event.away_team_id
                self.ball_possesion_team_id = event.home_team_id

                self.original_left_team_id = event.home_team_id
                self.original_right_team_id = event.away_team_id
                self.original_ball_possesion_team_id = event.home_team_id

        else:
            # 2nd event or more
            self.start_scheduled_epoch = str(int(Period._get_({"event_id": self.event_id, "status": 2})[-1].end_actual_epoch) + int(rules_set.interval_between_periods_munutes.split(";")[periods_count - 1]) * 60) #TODO check if we need to substract 2
 
            if self.left_team_id == -1 or self.right_team_id == -1 or self.ball_possesion_team_id == -1:
                self.left_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_left_team_id
                self.right_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_right_team_id
                self.ball_possesion_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_ball_possesion_team_id

                self.original_left_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_left_team_id
                self.original_right_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_right_team_id
                self.orgiginal_ball_possesion_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_ball_possesion_team_id

        if rules_set.periods_lenght_minutes.split(";")[periods_count - 1] == "0":
            self.end_scheduled_epoch = "0"
        else:
            self.end_scheduled_epoch = str(int(self.start_scheduled_epoch) + int(rules_set.periods_lenght_minutes.split(";")[periods_count - 1]) * 60)

        self.save()

        event.periods_ids = event.periods_ids + f"{self.id};"
        event.save()

        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *self.run()]

        return rv
                
    def end(self): #TODO JSON
        
        self.status = 2
        self.end_actual_epoch = int(time.time())
        self.save()

        event = Event._get_({"id": self.event_id})[0]
        event.status = 3
        event.save()

        admin = BotUser._get_({"id": event.admin_id})[0]

        home_team_name = Team._get_({"id": self.left_team_id})[0].name
        away_team_name = Team._get_({"id": self.right_team_id})[0].name

        period_count = len(Period._get_({"event_id": self.event_id}))

        Remainder.unschedule(f"period_{self.id}_end") # todo add for event in general as well

        rv = [*event.run(), *Remainder._get_("PeriodEnded").schedule(int(time.time()), event.admin_id, [[period_count, self.event_id, home_team_name, away_team_name], ], f"period_{period_count}_event_{self.event_id}_ended", [[self.id, ]])]

        if admin.show_screen_to("10", [[config("telebot_version")], ], ) not in rv:
            rv.append(admin.show_screen_to("10", [[config("telebot_version")], ], ))

        return rv

    def pause(self):
        
        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        period_count = len(Period._get_({"event_id": self.event_id}))

        if rules_set.timers_stop_at_pauses == 1: #TODO add for event timers as well
            Remainder.unschedule(f"period_{period_count}_event_{self.event_id}_end")

        self.is_paused = 1
        self.save()

    def resume(self):
        
        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        period_count = len(Period._get_({"event_id": self.event_id}))

        if rules_set.timers_stop_at_pauses == 1:
            Remainder.reschedule(f"period_{period_count}_event_{self.event_id}_end")

        self.is_paused = 0
        self.save()

    def launch(self):

        event = Event._get_({"id": self.event_id})[0]

        self.status = 1
        event.status = 2

        self.start_actual_epoch = int(time.time())
        if event.start_actual_epoch == "":
            event.start_actual_epoch = self.start_actual_epoch

        self.save()
        event.save()

    def run(self, command="_"): #TODO JSON
        
        rv = []

        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]

        left_team_name = Team._get_({"id": self.left_team_id})[0].name
        right_team_name = Team._get_({"id": self.right_team_id})[0].name

        period_count = len(Period.objects.filter(event_id=self.event_id))

        score = [0,0]
        for point_id in self.points_ids.split(";"):
            if point_id:
                point = Point._get_({"id": int(point_id)})[0]
                score[point.team_id != self.left_team_id] += point.value

        def tto_now(): #TODO move to utils
            
            total_technical_time_outs_this_period = len(TimeOut._get_({"event_id": self.event_id, "period_id": self.id, "is_technical": 1}))
            
            res = False

            for i, comma_scores in enumerate(rules_set.technical_time_outs_at_score_per_period.split(";")):
                if comma_scores:
                    try:
                        x, y = comma_scores.split(",")
                        if total_technical_time_outs_this_period == i:
                            if x == "0" or y == "0":
                                res = (score[0] == int(x) if x != "0" else int(y)) or (score[1] == int(x) if x != "0" else int(y))
                            else:
                                res = score[0] == int(x) and score[1] == int(y)
                        else:
                            continue
                    except:
                        sum_score = comma_scores
                        res = sum(score) == int(sum_score)

            return res

        def sc_now(): #TODO move to utils

            total_side_changes_this_period = len(SideChange._get_({"event_id": self.event_id, "period_id": self.id}))
            
            res = False

            if not rules_set.side_changes_during_periods.split(";")[period_count - 1] == "1":
                return False

            for i, comma_scores in enumerate(rules_set.side_changes_during_periods_scores.split(";")):
                if comma_scores:
                    try:
                        x, y = comma_scores.split(",")
                        if total_side_changes_this_period == i:
                            if x == "0" or y == "0":
                                res = (score[0] == int(x) if x != "0" else int(y)) or (score[1] == int(x) if x != "0" else int(y))
                            else:
                                res = score[0] == int(x) and score[1] == int(y)
                        else:
                            continue
                    except:
                        sum_score = comma_scores
                        res = sum(score) == int(sum_score)    

            return res        

        def check_remainders():
            
            def check_sent_already(remainder_id, group_name): #TODO JSON move to utils
                return len(ScheduledMessage._get_({"content_id": remainder_id, "group_name": group_name})) > 0
            
            if self.status == 0 and not check_sent_already(114, f"period_{period_count}_event_{self.event_id}_start"):   
                rv.extend(Remainder._get_("PeriodScheduled").schedule(int(time.time()), event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name] ,], f"period_{period_count}_event_{self.event_id}_start", [[self.id, self.id], ]))

            # check period start
            
            if self.status == 0 and not check_sent_already(110, f"period_{period_count}_event_{self.event_id}_start"):
                    
                when = int(self.start_scheduled_epoch)

                rv.extend(Remainder._get_("PeriodStart").schedule(when, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name] ,], f"period_{period_count}_event_{self.event_id}_start", [[self.id, self.id], ]))
    
                for offset in rules_set.period_start_remainder_minutes_before.split(";")[period_count - 1].split(","):
                    if offset:
                        rv.extend(Remainder._get_("PeriodAboutToStart").schedule(when - int(offset) * 60, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name, offset] ,], f"period_{period_count}_event_{self.id}_start", [[self.id, self.id], ]))

            # check period end

            if rules_set.periods_lenght_minutes.split(";")[period_count-1] != "0" and self.status == 1 and not check_sent_already(111, f"period_{period_count}_event_{self.event_id}_end"):
                    
                when = int(self.end_scheduled_epoch)
                
                rv.extend(Remainder._get_("PeriodEnd").schedule(when, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name] ,], f"period_{period_count}_event_{self.event_id}_end", [[self.id, self.id], ]))
    
                for offset in rules_set.period_end_remainder_minutes_before.split(";").split(",")[period_count - 1]:
                    if offset:
                        rv.extend(Remainder._get_("PeriodAboutToEnd").schedule(when - int(offset) * 60, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name, offset] ,], f"period_{period_count}_event_{self.event_id}_end", [[self.id, self.id], ]))

            # check side change reminders
            if self.status == 1 and sc_now() and not check_sent_already(150, f"event_{self.event_id}_side_change_during_period_{period_count}"):
                
                rv.extend((Remainder._get_("SideChangeHappens").schedule(int(time.time()), event.admin_id, [[] ,], f"event_{self.event_id}_side_change_during_period_{period_count}", [[], ])))

            # check time_out
            if data[0] == "timeOut":
                
                rv.extend(Remainder._get_("TimeOutStart").schedule(
                    int(time.time()), 
                    event.admin_id, 
                    [[left_team_name if data[1] == "0" else right_team_name, ],], 
                    f"period_{period_count}_event_{self.event_id}_time_out_team_{data[1]}_score_{score[0]}:{score[1]}", 
                    [["", f"period_{period_count}_event_{self.event_id}_time_out_team_{data[1]}_score_{score[0]}:{score[1]}",],] #TODO figure this out
                    ))
                
                rv.extend(Remainder._get_("TimeOutEnd").schedule(
                    int(time.time()) + int(rules_set.time_outs_lenghts_per_team_per_period.split(";")[period_count-1].split(',')[int(data[1])]), 
                    event.admin_id, 
                    [[left_team_name if data[1] == "0" else right_team_name, ],], 
                    f"period_{period_count}_event_{self.event_id}_time_out_team_{data[1]}_score_{score[0]}:{score[1]}", 
                    [[self.id, ],[self.id, ]])) #TODO and this

            # check tehcnical time out
            if self.status == 1 and tto_now() and not check_sent_already(130, f"period_{period_count}_event_{self.event_id}_technical_time_out_score_{score[0]}:{score[1]}"):
                
                rv.extend(Remainder._get_("TechnicalTimeOutStart").schedule(
                    int(time.time()), 
                    event.admin_id, 
                    [[] ,], 
                    f"period_{period_count}_event_{self.event_id}_technical_time_out_score_{score[0]}:{score[1]}", 
                    [["", f"period_{period_count}_event_{self.event_id}_technical_time_out_score_{score[0]}:{score[1]}",],] #TODO figure this out
                    ))
                
                rv.extend(Remainder._get_("TechnicalTimeOutEnd").schedule(
                    int(time.time()) + int(rules_set.technical_time_outs_lenghts_per_period.split(";")[period_count-1]), 
                    event.admin_id, 
                    [[] ,], 
                    f"period_{period_count}_event_{self.event_id}_technical_time_out_score_{score[0]}:{score[1]}", 
                    [[self.id, ], [self.id, ]])) #TODO and this

        def check_period_end():

            one = rules_set.win_period_by.split(";")[period_count - 1] == "1"
            two = (max(score) >= int(rules_set.points_to_win_period.split(";")[period_count - 1]) and rules_set.stop_period_after_enough_points.split(";")[period_count - 1] == "1")
            three = (rules_set.points_in_period == 0) or max(score) >= int(rules_set.points_in_period.split(";")[period_count - 1])
            four = max(score) - min(score) >= int(rules_set.min_difference_points_to_win_period.split(";")[period_count - 1])

            rv = one and two and three and four

            return rv 

        def check_technical_time_out():

            return self.status == 1 and tto_now() and len(TimeOut._get_({"is_technical": 1, "event_id": self.event_id, "period_id": self.id, "at_score": f"{score[0]}:{score[1]}"})) == 0

        def check_time_out():
            return data[0] == "timeOut"

        def check_side_change():
            return self.status == 1 and sc_now() and len(SideChange._get_({"event_id": self.event_id, "period_id": self.id, "at_score": f"{score[0]}:{score[1]}"})) == 0

        def check_action():
            return data[0] == "action"

        def check_point():
            return data[0] == "point"

        def check_pause_resume():
            return data[0] == "pauseResume"

        def check_ball_control():
            return data[0] == "ballControl"

        def check_show():
            return data[0] == "show"

        data = command.split("_")

        if check_point(): #point_team_type
            
            point_ = Point()
            point_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, f"{score[0]}:{score[1]}", data[2])            
            point_.value = rules_set.points_per_score_per_period.split(";")[period_count-1].split(",")[point_.team_id != self.left_team_id]
            point_.save()

            score[int(data[1])] += int(point_.value)

            self.points_ids = f"{self.points_ids}{point_.id};" #TODO figure out why this is not working inside happen function and make consistant
            self.save()

        check_remainders()

        if check_period_end():
            rv.extend(self.end())
            
            return rv

        if check_pause_resume():
            
            if self.is_paused == 0:
                self.pause()
                rv.extend(event.show_paused_match_template(self.id))
            else:
                self.resume()
                rv.extend(event.show_match_template(self.id))

        if check_side_change():

            side_change_ = SideChange()
            side_change_.save()

            side_change_.happen(self.event_id, self.id, f"{score[0]}:{score[1]}")
            side_change_.save()

            rv.extend(event.show_match_template(self.id))

        if check_technical_time_out() and not check_side_change(): #TODO fix (rules)

            self.pause()

            tto_ = TimeOut()
            tto_.is_technical = 1
            tto_.save()

            tto_.happen(self.event_id, self.id, -1, f"{score[0]}:{score[1]}")

            rv.extend(event.show_paused_match_template(self.id))

        if check_time_out():

            self.pause()

            to_ = TimeOut()
            to_.save()

            to_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, f"{score[0]}:{score[1]}")
            to_.save()
            
            rv.extend(event.show_paused_match_template(self.id))

        if check_action():

            action_ = Action()
            action_.save()

            action_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, int(data[2]), f"{score[0]}:{score[1]}")
            action_.save()

            rv.extend(event.show_match_template(self.id))

        if check_ball_control():

            self.ball_possesion_team_id = self.left_team_id if data[1] == "0" else self.right_team_id if data[1] == "2" else -1
            self.save()

            rv.extend(event.show_match_template(self.id))

        if check_show() or len(rv) == 0:

            if self.is_paused:
                rv.extend(event.show_paused_match_template(self.id))
            else:
                rv.extend(event.show_match_template(self.id))

        return rv

    def cancel(self): #TODO JSON
        pass

class Team(LogicModel):
    
    name = models.CharField(max_length=5096, default="")
    events_ids = models.CharField(max_length=5096, default=";") 

class Competition(LogicModel):

    name = models.CharField(max_length=5096, default="")
    events_ids = models.CharField(max_length=5096, default=";")

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

class Action(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)
    type_id = models.IntegerField(default=-1)

    epoch_time = models.CharField(max_length=5096, default="")

    at_score = models.CharField(max_length=5096, default="")

    def happen(self, event_id, period_id, team_id, type_id, at_score):
        
        self.event_id = event_id
        self.period_id = period_id
        self.team_id = team_id
        self.type_id = type_id
        self.at_score = at_score
        self.epoch_time = str(time.time())
        self.save()

        period = Period._get_({"id": self.period_id})[0]
        period.actions_ids = period.actions_ids + str(self.id) + ";"
        period.save()

    def cancel_happen(self):
        
        self.status = 0
        self.save()
        
        period = Period._get_({"id": self.period_id})[0]
        period.actions_ids.pop(f";{self.id};")
        period.save()

        period.cancel("")

class CoinToss(LogicModel):
    
    event_id = models.IntegerField(default=-1)

    epoch_scheduled = models.CharField(max_length=5096, default="")
    epoch_actual = models.CharField(max_length=5096, default="") 

    before_period = models.IntegerField(default=1)

    left_team_id = models.IntegerField(default=0)
    ball_possesion_team_id = models.IntegerField(default=0)

    def happen(self, event_id, epoch_scheduled, before_period, team_id):
        
        self.event_id = event_id
        self.epoch_scheduled = epoch_scheduled
        self.before_period = before_period
        self.left_team_id = team_id
        self.ball_possesion_team_id = team_id

        self.save()

    def swipe(self, attr):

        event = Event._get_({"id": self.event_id})[0]

        setattr(self, attr, event.away_team_id if getattr(self, attr) == event.home_team_id else event.home_team_id)

        self.save()
        return self.show_template()

    def save_results(self):
        
        event = Event._get_({"id": self.event_id})[0]

        self.epoch_actual = str(time.time())
        self.save()

        new_period = Period()
        new_period.event_id = self.event_id
        
        new_period.left_team_id = self.left_team_id
        new_period.right_team_id = (event.home_team_id if self.left_team_id == event.away_team_id else event.away_team_id)
        new_period.ball_possesion_team_id = self.ball_possesion_team_id
        
        new_period.original_left_team_id = self.left_team_id
        new_period.original_right_team_id = (event.home_team_id if self.left_team_id == event.away_team_id else event.away_team_id)
        new_period.original_ball_possesion_team_id = self.ball_possesion_team_id

        new_period.save()

        return new_period.start() 
        
    def cancel_happen(self):
        pass

    def cancel_edit(self):
        pass

    def cancel_save(self):
        pass

    def show_template(self):

        event = Event._get_({"id": self.event_id})[0]
        admin = BotUser._get_({"id": event.admin_id})[0]
        
        left_team_name = Team._get_({"id": self.left_team_id})[0].name
        server_name = Team._get_({"id": self.ball_possesion_team_id})[0].name

        rv = []
        rv.append(admin.show_screen_to("32", [[self.event_id, self.before_period, left_team_name, server_name], ], [[self.id, self.id, self.id, self.id], ]))
        rv.append(("ignore", 32))
        return rv

class Point(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)

    at_score = models.CharField(max_length=5096, default="")
    
    epoch_time = models.CharField(max_length=5096, default="")

    type = models.IntegerField(default=-1)
    value = models.IntegerField(default=1)

    def happen(self, event_id, period_id, team_id, at_score, type):
        
        self.event_id = event_id
        self.period_id = period_id
        self.team_id = team_id
        self.at_score = at_score
        self.type = type
        self.epoch_time = str(time.time())
        self.save()

    def cancel_happen(self):
        pass 

class SideChange(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)

    at_score = models.CharField(max_length=5096, default="")

    epoch_time = models.CharField(max_length=5096, default="")

    left_team_after_id = models.IntegerField(default=-1)

    def happen(self, event_id, period_id, at_score):
            
        self.event_id = event_id
        self.period_id = period_id
        self.at_score = at_score

        self.save()

        if self.period_id == -1:
            
            period = Period._get_({"event_id": self.event_id, "status": 0})[0]
            period.left_team_id, period.right_team_id = period.right_team_id, period.left_team_id
            period.original_left_team_id, period.original_right_team_id = period.original_right_team_id, period.original_left_team_id
            period.save()

            event = Event._get_({"id": self.event_id})[0]
            event.side_changes_ids += f"{self.id};"
            event.save()

        else:
            period = Period._get_({"id": self.period_id})[0]
            period.left_team_id, period.right_team_id = period.right_team_id, period.left_team_id
            period.side_changes_ids = period.side_changes_ids + str(self.id) + ";"
            period.save()

        self.left_team_after_id = period.left_team_id
        self.epoch_time = str(time.time())
        self.save()

    def cancel_happen(self):
        pass

class TimeOut(LogicModel):

    is_technical = models.IntegerField(default=0)

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)
    
    at_score = models.CharField(max_length=5096, default="")

    epoch_time = models.CharField(max_length=5096, default="")

    def happen(self, event_id, period_id, team_id, at_score):
        
        self.event_id = event_id
        self.period_id = period_id
        self.team_id = team_id
        self.at_score = at_score
        self.epoch_time = str(time.time())
        self.save()

        period = Period._get_({"id":self.period_id})[0]
        period.timeouts_ids = period.timeouts_ids + str(self.id) + ";"
        period.save()

    def cancel_happen(self):
        pass

# TELEBOT
class PasswordPair(models.Model):
    
    password_sha256 = models.CharField(max_length=5096)
    user_id = models.IntegerField(default=-1)

    #def generate(self, string): #TODO connect (via superadmin commands?)
    #   self.password_sha256 = hashlib.sha256(string.encode('utf8')).hexdigest()
    #   self.save()
    
    def assign_to_user(self, user_id):
        
        self.user_id = user_id

        users = BotUser.objects.all()
        for user in users:
            if user.id == user_id:
                user.password_id = self.id
                user.save()
        
        self.save()

class BotUser(models.Model):

    tg_id = models.CharField(max_length=5096, blank=True)
    language_id = models.IntegerField(default=0)

    password_id = models.IntegerField(default=-1)
    is_logged_in = models.IntegerField(default=0)
    is_superadmin = models.IntegerField(default=0)

    current_screen_code = models.CharField(max_length=5096, default="00")

    screen_messages_ids = models.CharField(max_length=5096, default=f"{{}}")
    remainders_ids = models.CharField(max_length=5096, default=f"{{}}")
    user_input_messages_ids = models.CharField(max_length=5096, default=f"{{}}")

    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    def check_authorization(self, ignore_authorization_screens=False):
        return self.is_logged_in or ((self.current_screen_code == "00" or self.current_screen_code == "01") and ignore_authorization_screens)

    def receive_text_from(self, text):
        
        if not self.check_authorization(True):
            return self.show_screen_to("00")       

        screen = Screen._get_(id=self.current_screen_code)
            
        return None if not hasattr(screen, "text") else screen.text(text, self.id) 

    def receive_command_from(self, command):
        if not self.check_authorization():
            return self.show_screen_to("00")       

        if command == "/start":
            return self.show_screen_to("10", [[config("telebot_version")], ]) #TODO move static formatters into screen class?
        elif command.startswith('/show_screen'):
            return self.show_screen_to(*command.split(" ")[1:]) if self.is_superadmin else None
        else:    
            return self.receive_text_from(command)

    def receive_button_press_from(self, button_id, params, screen_type, screen_id="", scheduled_message_id=None):
        
        if not self.check_authorization():
            return self.show_screen_to("00")       
        
        if screen_type == "screen":
            
            screen = Screen._get_(id=self.current_screen_code if screen_id == "" else str(screen_id))

            return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id)

        elif screen_type == "remainder":

            screen = Remainder._get_(remainder_id=str(screen_id))
            return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id, scheduled_message_id)

    def show_screen_to(self, screen_id, format_strs=None, callback_data=None):
        self.current_screen_code = screen_id
        self.save()
        return [screen_id, "screen", format_strs, callback_data]

    def send_remainder_to(self, remainder_id, epoch, format_strs=None, group="", callback_data=None):
        return [remainder_id, "remainder", epoch, format_strs, group, callback_data]

    def show_list_of_events(self, flush_safe=False):

        status_strings = []
        for text_string in TextString.objects.all().order_by("id"):
            if text_string.screen_id == "status":
                status_strings.append([text_string.language_1, text_string.language_2, text_string.language_3, text_string.language_4, text_string.language_5])

        rv = []

        for event in Event.objects.all():

            if event.admin_id == self.id: # TODO change to inline if-then (look Event.show_layout)
                
                try:
                    home_team_name = Team._get_({"id": event.home_team_id})[0].name
                except:
                    home_team_name = ""

                try:
                    away_team_name = Team._get_({"id": event.away_team_id})[0].name
                except:
                    away_team_name = ""

                try:
                    competition_name = Competition._get_({"id": event.competition_id}).name
                except:
                    competition_name = ""

                try:
                    rules_set_name = RulesSet.objects.get(pk=event.rules_set_id).name
                except: 
                    rules_set_name = ""

                try:
                    date = event.date_scheduled
                except:
                    date = ""

                try:
                    time_ = event.time_scheduled
                except:
                    time_ = ""

                if event.active_status == 1:
                    rv.append(self.show_screen_to("43", [[event.id, status_strings[event.status][self.language_id], home_team_name, away_team_name, competition_name, rules_set_name, date, time_]], [[event.id, event.id],]))
                else:
                    rv.append(self.show_screen_to("44", [[event.id, status_strings[5][self.language_id], home_team_name, away_team_name, competition_name, rules_set_name, date, time_]], [[event.id, event.id],]))

        if len(rv) > 0:
            rv.append(self.show_screen_to("40", [[], ]))
        else: 
            rv.append(self.show_screen_to("41", [[], ]))

        if flush_safe: rv.append(("ignore", 40, 43, 44))

        return rv

class ScheduledMessage(models.Model):

    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    user_id = models.IntegerField(default=-1)
    messages_ids = models.CharField(max_length=5096, default=";")

    epoch = models.CharField(max_length=5096, default="")
    pause_epoch = models.CharField(max_length=5096, default="")

    content_type = models.CharField(max_length=5096, default="remainder")
    content_id = models.IntegerField(default=-1)
    content_formatters = models.CharField(max_length=5096, default="")
    content_callback = models.CharField(max_length=5096, default="")

    is_sent = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)

    group_name = models.CharField(max_length=5096, default="")

# LOCALIZATION
class TextString(models.Model): #TODO make connection with outside dictionary

    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    screen_id = models.CharField(max_length=5096, default="")
    position_index = models.IntegerField(default=-1)

    language_1 = models.CharField(max_length=5096, blank=True)
    language_2 = models.CharField(max_length=5096, blank=True)
    language_3 = models.CharField(max_length=5096, blank=True)
    language_4 = models.CharField(max_length=5096, blank=True)
    language_5 = models.CharField(max_length=5096, blank=True)

class TextLanguage(models.Model):

    self_name = models.CharField(max_length=5096, default="")
