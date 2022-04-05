from decouple import config

from django.db import models

import time

from ...bin.utils import Utils

from ...screens.remainders.Remainder import Remainder

from .LogicModel import LogicModel


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

        from .event.Event import Event

        from .RulesSet import RulesSet
        
        from ..telebot.BotUser import BotUser

        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        admin = BotUser._get_({"id": event.admin_id})[0]
       
        periods_count = len(Period._get_({"event_id": self.event_id}))
        
        self.status = 0

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

        Utils.api("period_scheduled", "logic", period_id=self.id, period_epoch=int(self.start_scheduled_epoch), period_count=periods_count, event_id=self.event_id)

        return rv
                
    def end(self): #TODO JSON
        
        from .event.Event import Event

        from .Team import Team

        from ..telebot.BotUser import BotUser

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

        Utils.api("period_ended", "logic", period_id=self.id, period_count=len(Period._get_({"event_id": self.event_id})), event_id=self.event_id)

        rv = [*event.run(), *Remainder._get_("PeriodEnded").schedule(int(time.time()), event.admin_id, [[period_count, self.event_id, home_team_name, away_team_name], ], f"period_{period_count}_event_{self.event_id}_ended", [[self.id, ]])]

        if admin.show_screen_to("10", [[config("telebot_version")], ], ) not in rv:
            rv.append(admin.show_screen_to("10", [[config("telebot_version")], ], ))

        return rv

    def pause(self):
        
        from .event.Event import Event

        from .RulesSet import RulesSet

        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        period_count = len(Period._get_({"event_id": self.event_id}))

        if rules_set.timers_stop_at_pauses == 1: #TODO add for event timers as well
            Remainder.unschedule(f"period_{period_count}_event_{self.event_id}_end")
        
        Utils.api("period_paused", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id)
            
        self.is_paused = 1
        self.save()

    def resume(self):
        
        from .event.Event import Event

        from .RulesSet import RulesSet

        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        period_count = len(Period._get_({"event_id": self.event_id}))

        if rules_set.timers_stop_at_pauses == 1:
            Remainder.reschedule(f"period_{period_count}_event_{self.event_id}_end")

        Utils.api("period_resumed", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id)

        self.is_paused = 0
        self.save()

    def launch(self):

        from .event.Event import Event

        event = Event._get_({"id": self.event_id})[0]

        self.status = 1
        event.status = 2

        self.start_actual_epoch = int(time.time())
        if event.start_actual_epoch == "":
            event.start_actual_epoch = self.start_actual_epoch
            Utils.api("event_started", "logic", event_id=self.event_id)

        Utils.api("period_started", "logic", period_id=self.id, period_count=len(Period._get_({"event_id": self.event_id})), event_id=self.event_id)

        self.save()
        event.save()

    def run(self, command="_"): #TODO JSON
        
        rv = []

        from .event.Event import Event

        from .RulesSet import RulesSet
        from .Team import Team
        from .Point import Point
        from .TimeOut import TimeOut
        from .SideChange import SideChange
        from .Action import Action

        from ..telebot.ScheduledMessage import ScheduledMessage

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
                    f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}", 
                    [["", f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}",],] #TODO figure this out
                    ))
                
                rv.extend(Remainder._get_("TimeOutEnd").schedule(
                    int(time.time()) + int(rules_set.time_outs_lenghts_per_team_per_period.split(";")[period_count-1].split(',')[int(data[1])]), 
                    event.admin_id, 
                    [[left_team_name if data[1] == "0" else right_team_name, ],], 
                    f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}", 
                    [[ f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}", ], ])) #TODO and this

            # check tehcnical time out
            if self.status == 1 and tto_now() and not check_sent_already(130, f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}"):
                
                rv.extend(Remainder._get_("TechnicalTimeOutStart").schedule(
                    int(time.time()), 
                    event.admin_id, 
                    [[] ,], 
                    f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}", 
                    [["", f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}",],] #TODO figure this out
                    ))
                
                rv.extend(Remainder._get_("TechnicalTimeOutEnd").schedule(
                    int(time.time()) + int(rules_set.technical_time_outs_lenghts_per_period.split(";")[period_count-1]), 
                    event.admin_id, 
                    [[] ,], 
                    f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}", 
                    [[f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}",],])) #TODO and this

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

            Utils.api("point_happened", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, team_id=point_.team_id, point_type=int(data[2]), point_value=point_.value, team_score=score[int(data[1])])

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

            Utils.api("side_change_during_period_happened", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, side_change_id=side_change_.id)

            rv.extend(event.show_match_template(self.id))

        if check_technical_time_out() and not check_side_change(): #TODO fix (rules)

            self.pause()

            tto_ = TimeOut()
            tto_.is_technical = 1
            tto_.save()

            tto_.happen(self.event_id, self.id, -1, f"{score[0]}:{score[1]}")

            Utils.api("technical_time_out_started", "logic", period_count=period_count, time_out_id=tto_.id, event_id=self.event_id, period_id=self.id)


            rv.extend(event.show_paused_match_template(self.id))

        if check_time_out():

            self.pause()

            to_ = TimeOut()
            to_.save()

            to_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, f"{score[0]}:{score[1]}")
            to_.save()
            
            Utils.api("time_out_started", "logic", period_count=period_count, time_out_id=to_.id, event_id=self.event_id, team_id=self.left_team_id if data[1] == "0" else self.right_team_id, period_id=self.id)

            rv.extend(event.show_paused_match_template(self.id))

        if check_action():

            action_ = Action()
            action_.save()

            action_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, int(data[2]), f"{score[0]}:{score[1]}")
            action_.save()

            Utils.api("action_happened", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, action_id=action_.id, team_id=self.left_team_id if data[1] == "0" else self.right_team_id, action_type=int(data[2]))

            rv.extend(event.show_match_template(self.id))

        if check_ball_control(): #TODO make new model (BallControlChange)

            self.ball_possesion_team_id = self.left_team_id if data[1] == "0" else self.right_team_id if data[1] == "2" else -1
            self.save()

            Utils.api("ball_possesion_changed", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, possession_index=int(data[1]))

            rv.extend(event.show_match_template(self.id))

        if check_show() or len(rv) == 0:

            if self.is_paused:
                rv.extend(event.show_paused_match_template(self.id))
            else:
                rv.extend(event.show_match_template(self.id))

        return rv

    def cancel(self): #TODO JSON
        pass