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

        print(400)

        from .event.Event import Event

        from .RulesSet import RulesSet
        
        from ..telebot.BotUser import BotUser

        print(401)

        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        admin = BotUser._get_({"id": event.admin_id})[0]
       
        print(402)

        periods_count = len(Period._get_({"event_id": self.event_id}))
        
        print(403)

        self.status = 0

        print(404)

        if periods_count == 1:
            # 1st event
            self.start_scheduled_epoch = event.start_scheduled_epoch

            print(405)
            if self.left_team_id == -1 or self.right_team_id == -1 or self.ball_possesion_team_id == -1:
                self.left_team_id = event.home_team_id
                self.right_team_id = event.away_team_id
                self.ball_possesion_team_id = event.home_team_id

                print(406)
                self.original_left_team_id = event.home_team_id
                self.original_right_team_id = event.away_team_id
                self.original_ball_possesion_team_id = event.home_team_id

        else:
            print(407)
            # 2nd event or more
            try:
                self.start_scheduled_epoch = str(int(Period._get_({"event_id": self.event_id, "status": 2})[-1].end_actual_epoch) + int(rules_set.interval_between_periods_minutes[periods_count - 2]) * 60)
            except Exception as e:
                print(e)

            print(408)
            if self.left_team_id == -1 or self.right_team_id == -1 or self.ball_possesion_team_id == -1:
                self.left_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_left_team_id
                self.right_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_right_team_id
                self.ball_possesion_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_ball_possesion_team_id

                print(409)
                self.original_left_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_left_team_id
                self.original_right_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_right_team_id
                self.original_ball_possesion_team_id = Period._get_({"event_id": self.event_id, "status": 2})[-1].original_ball_possesion_team_id

        print(410)
        if rules_set.periods_lenght_minutes[periods_count - 1] == 0:
            self.end_scheduled_epoch = "0"
        else:
            self.end_scheduled_epoch = str(int(self.start_scheduled_epoch) + int(rules_set.periods_lenght_minutes[periods_count - 1]) * 60)

        print(411)
        self.save()

        print(412)
        event.periods_ids = event.periods_ids + f"{self.id};"
        event.save()

        print(413)
        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *self.run()]
            
        print(414)
        Utils.api("period_scheduled", "logic", period_id=self.id, period_epoch=int(self.start_scheduled_epoch), period_count=periods_count, event_id=self.event_id)
        print(415)
        return rv
                
    def end(self): #TODO JSON
        
        print(200)

        from .event.Event import Event

        from .Team import Team

        from ..telebot.BotUser import BotUser

        print(201)

        self.status = 2
        self.end_actual_epoch = int(time.time())
        self.save()

        print(202)

        event = Event._get_({"id": self.event_id})[0]
        event.status = 3
        event.save()

        print(203)

        admin = BotUser._get_({"id": event.admin_id})[0]

        print(204)

        home_team_name = Team._get_({"id": self.left_team_id})[0].name
        away_team_name = Team._get_({"id": self.right_team_id})[0].name

        print(205)

        period_count = len(Period._get_({"event_id": self.event_id}))

        print(206)

        Remainder.unschedule(f"period_{self.id}_end") # todo add for event in general as well

        print(207)

        Utils.api("period_ended", "logic", period_id=self.id, period_count=len(Period._get_({"event_id": self.event_id})), event_id=self.event_id)

        print(208)

        rv = [*event.run(), *Remainder._get_("PeriodEnded").schedule(int(time.time()), event.admin_id, [[period_count, self.event_id, home_team_name, away_team_name], ], f"period_{period_count}_event_{self.event_id}_ended", [[self.id, ]])]

        print(209)

        if admin.show_screen_to("10", [[config("telebot_version")], ], ) not in rv:
            rv.append(admin.show_screen_to("10", [[config("telebot_version")], ], ))

        print(210)

        return rv

    def pause(self):
        
        from .event.Event import Event

        from .RulesSet import RulesSet

        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        period_count = len(Period._get_({"event_id": self.event_id}))

        if rules_set.period_timers_stop_at_pauses[period_count - 1] == 1: #TODO add for event timers as well
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

        if rules_set.period_timers_stop_at_pauses[period_count - 1] == 1:
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
        
        try:
            
            print(1)

            rv = []

            print(2)

            from .event.Event import Event

            from .RulesSet import RulesSet
            from .Team import Team
            from .Point import Point
            from .TimeOut import TimeOut
            from .SideChange import SideChange
            from .Action import Action

            from ..telebot.ScheduledMessage import ScheduledMessage

            print(3)

            event = Event._get_({"id": self.event_id})[0]
            rules_set = RulesSet._get_({"id": event.rules_set_id})[0]

            print(4)

            left_team_name = Team._get_({"id": self.left_team_id})[0].name
            right_team_name = Team._get_({"id": self.right_team_id})[0].name

            print(5)

            period_count = len(Period.objects.filter(event_id=self.event_id))

            print(6)

            score = [0,0]
            for point_id in self.points_ids.split(";"):
                if point_id:
                    point = Point._get_({"id": int(point_id)})[0]
                    score[0 if int(point.team_id) == int(self.left_team_id) else 1] += point.value
                    score[1 if int(point.team_id) == int(self.left_team_id) else 0] += point.opposite_value

            print(7)

            def tto_now(): #TODO move to utils
                
                print(8)

                total_technical_time_outs_this_period = len(TimeOut._get_({"event_id": self.event_id, "period_id": self.id, "is_technical": 1}))
                
                print(9)

                res = False

                print(10)

                print("id", self.id)
                print(score, rules_set.technical_time_outs_at_score_per_period, period_count, total_technical_time_outs_this_period)
                for i, comma_scores in enumerate(rules_set.technical_time_outs_at_score_per_period[period_count-1]):
                    print(comma_scores, i)
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
                        except Exception as e:
                            print(e)
                            sum_score = comma_scores
                            res = sum(score) == int(sum_score)

                print(11)

                return res

            def sc_now(): #TODO move to utils

                print(12)

                total_side_changes_this_period = len(SideChange._get_({"event_id": self.event_id, "period_id": self.id}))
                
                print(13)

                res = False

                print(14)

                if not len(rules_set.side_changes_during_periods[period_count - 1]) > 0:
                    return False

                print(15)
                print(rules_set.side_changes_during_periods, period_count, total_side_changes_this_period)
                for i, comma_scores in enumerate(rules_set.side_changes_during_periods[period_count-1]):
                    print(15.1)
                    if comma_scores:
                        print(15.2)
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

                print(16)

                return res        

            def check_remainders():

                print(17)

                def check_sent_already(remainder_id, group_name): #TODO JSON move to utils
                    return len(ScheduledMessage._get_({"content_id": remainder_id, "group_name": group_name})) > 0
                
                print(18)

                if self.status == 0 and not check_sent_already(114, f"period_{period_count}_event_{self.event_id}_start"):   
                    rv.extend(Remainder._get_("PeriodScheduled").schedule(int(time.time()), event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name] ,], f"period_{period_count}_event_{self.event_id}_start", [[self.id, self.id], ]))

                # check period start
                
                print(19)

                if self.status == 0 and not check_sent_already(110, f"period_{period_count}_event_{self.event_id}_start"):
                    
                    when = int(self.start_scheduled_epoch)

                    rv.extend(Remainder._get_("PeriodStart").schedule(when, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name] ,], f"period_{period_count}_event_{self.event_id}_start", [[self.id, self.id], ]))

                    for offset in rules_set.period_start_remainder_minutes_before[period_count - 1]:
                        if offset:
                            rv.extend(Remainder._get_("PeriodAboutToStart").schedule(when - int(offset) * 60, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name, offset] ,], f"period_{period_count}_event_{self.id}_start", [[self.id, self.id], ]))

                print(20)

                # check period end
                if rules_set.periods_lenght_minutes[period_count-1] != 0 and self.status == 1 and not check_sent_already(111, f"period_{period_count}_event_{self.event_id}_end"):
                        
                    when = int(self.end_scheduled_epoch)
                    
                    rv.extend(Remainder._get_("PeriodEnd").schedule(when, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name] ,], f"period_{period_count}_event_{self.event_id}_end", [[self.id, self.id], ]))
        
                    for offset in rules_set.period_end_remainder_minutes_before[period_count - 1]:
                        if offset:
                            rv.extend(Remainder._get_("PeriodAboutToEnd").schedule(when - int(offset) * 60, event.admin_id, [[period_count, self.event_id, left_team_name, right_team_name, offset] ,], f"period_{period_count}_event_{self.event_id}_end", [[self.id, self.id], ]))

                print(21)

                # check side change reminders
                if self.status == 1 and sc_now() and not check_sent_already(150, f"event_{self.event_id}_side_change_during_period_{period_count}"):
                    
                    rv.extend((Remainder._get_("SideChangeHappens").schedule(int(time.time()), event.admin_id, [[] ,], f"event_{self.event_id}_side_change_during_period_{period_count}", [[], ])))

                print(22)

                # check time_out
                if data[0] == "timeOut":
                    
                    time_out_count = len(TimeOut._get_({"event_id": self.event_id, "period_id": self.id, "team_id": self.left_team_id if data[1] == "0" else self.right_team_id}))

                    rv.extend(Remainder._get_("TimeOutStart").schedule(
                        int(time.time()), 
                        event.admin_id, 
                        [[left_team_name if data[1] == "0" else right_team_name, ],], 
                        f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}", 
                        [["", f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}",],] #TODO figure this out
                        ))
                    
                    rv.extend(Remainder._get_("TimeOutEnd").schedule(
                        int(time.time()) + int(rules_set.time_outs_lenghts_per_team_per_period[int(data[1])][period_count - 1][time_out_count]), 
                        event.admin_id, 
                        [[left_team_name if data[1] == "0" else right_team_name, ],], 
                        f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}", 
                        [[ f"period_{period_count}_event_{self.event_id}_timeOutTeam_{data[1]}_score_{score[0]}:{score[1]}", ], ])) #TODO and this

                print(23)

                # check tehcnical time out
                if self.status == 1 and tto_now() and not check_sent_already(130, f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}"):
                    
                    time_out_count = len(TimeOut._get_({"event_id": self.event_id, "period_id": self.id, "is_technical": 1}))

                    rv.extend(Remainder._get_("TechnicalTimeOutStart").schedule(
                        int(time.time()), 
                        event.admin_id, 
                        [[] ,], 
                        f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}", 
                        [["", f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}",],] #TODO figure this out
                        ))
                    
                    rv.extend(Remainder._get_("TechnicalTimeOutEnd").schedule(
                        int(time.time()) + int(rules_set.technical_time_outs_lenghts_per_period[period_count-1][time_out_count]), 
                        event.admin_id, 
                        [[] ,], 
                        f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}", 
                        [[f"period_{period_count}_event_{self.event_id}_technicalTimeOutScore_{score[0]}:{score[1]}",],])) #TODO and this

            def check_period_end():
                #TODO check flow for 0

                print(24)

                one = rules_set.win_period_by[period_count - 1] == 1
                
                print(25)

                two = (rules_set.points_to_win_period[period_count - 1] > 0 and max(score) >= int(rules_set.points_to_win_period[period_count - 1]) and rules_set.stop_period_after_enough_points[period_count - 1] == 1)
                five = (rules_set.points_to_win_period[period_count - 1] == 0 and rules_set.stop_period_after_enough_points[period_count - 1] == 1)

                print(26)

                three = (rules_set.points_in_period[period_count - 1] == 0) or max(score) >= int(rules_set.points_in_period[period_count - 1])
                four = max(score) - min(score) >= int(rules_set.min_difference_points_to_win_period[period_count - 1])

                print(27)

                rv = one and (two or five) and three and four

                print(28)

                return rv 

            def check_technical_time_out():

                print(29)

                return self.status == 1 and tto_now() and len(TimeOut._get_({"is_technical": 1, "event_id": self.event_id, "period_id": self.id, "at_score": f"{score[0]}:{score[1]}"})) == 0

            def check_time_out():

                print(30)

                return data[0] == "timeOut"

            def check_side_change():

                print(31)

                return self.status == 1 and sc_now() and len(SideChange._get_({"event_id": self.event_id, "period_id": self.id, "at_score": f"{score[0]}:{score[1]}"})) == 0

            def check_action():

                print(32)

                return data[0] == "action"

            def check_point():

                print(33)

                return data[0] == "point"

            def check_pause_resume():

                print(34)

                return data[0] == "pauseResume"

            def check_ball_control():
                
                print(35)

                return data[0] == "ballControl"

            def check_show():

                print(36)

                return data[0] == "show"

            print(37)

            data = command.split("_")

            print(38)

            if check_point(): #point_team_type
                
                print(39)

                def check_ball_possession_change():    

                    print(40)    
                    if rules_set.ball_control_after_score_per_score[int(data[2])] == 0 and int(self.ball_possesion_team_id) != int(point_.team_id):
                        self.ball_possesion_team_id = self.left_team_id if data[1] == "0" else self.right_team_id
                        Utils.api("ball_possesion_changed", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, possession_index=int(data[1]))
                    elif rules_set.ball_control_after_score_per_score[int(data[2])] == 1 and (int(self.ball_possesion_team_id) == int(point_.team_id) or self.ball_possesion_team_id == -1):
                        self.ball_possesion_team_id = self.left_team_id if data[1] == "1" else self.right_team_id
                        Utils.api("ball_possesion_changed", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, possession_index=int(data[1]))
                    elif rules_set.ball_control_after_score_per_score[int(data[2])] == 2:
                        self.ball_possesion_team_id = -1
                        Utils.api("ball_possesion_changed", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, possession_index=int(data[1]))

                def check_event_pause():
                    print(41)
                    if rules_set.pause_after_score_per_score[int(data[2])] == 1 and self.is_paused == 0:
                        self.pause()
                        rv.extend(event.show_paused_match_template(self.id))

                print(42)

                point_ = Point()
                point_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, f"{score[0]}:{score[1]}", data[2])            
                point_.value = rules_set.points_per_period_per_score_per_team[period_count-1][int(data[2])][0]
                point_.opposite_value = rules_set.points_per_period_per_score_per_team[period_count-1][int(data[2])][1]
                point_.save()

                print(43)

                score[int(data[1])] += int(point_.value)
                score[1 if data[1] == "0" else 0] += int(point_.opposite_value)
            
                print(44)

                check_ball_possession_change()
                check_event_pause()

                print(45)

                Utils.api("point_happened", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, team_id=point_.team_id, point_type=int(data[2]), point_value=point_.value, opposite_point_value=point_.opposite_value, new_team_score=score[int(data[1])], new_opposite_team_score=score[1 if data[1] == "0" else 0])

                print(46)

                self.points_ids = f"{self.points_ids}{point_.id};" #TODO figure out why this is not working inside happen function and make consistant
                self.save()

                print(47)

            check_remainders()

            print(48)

            if check_period_end():
                print(28.5)
                rv.extend(self.end())
                print(49)
                return rv

            if check_pause_resume():
                print(50)

                if self.is_paused == 0:
                        
                    self.pause()
                    rv.extend(event.show_paused_match_template(self.id))
                    
                else:
                        
                    self.resume()
                    rv.extend(event.show_match_template(self.id))

            if check_side_change():

                print(51)

                side_change_ = SideChange()
                side_change_.save()

                print(52)

                side_change_.happen(self.event_id, self.id, f"{score[0]}:{score[1]}")
                side_change_.save()

                print(53)

                Utils.api("side_change_during_period_happened", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, side_change_id=side_change_.id)

                print(54)

                rv.extend(event.show_match_template(self.id))

                print(55)

            if check_technical_time_out() and not check_side_change(): #TODO fix (rules)

                print(56)
                self.pause()

                print(57)
                tto_ = TimeOut()
                tto_.is_technical = 1
                tto_.save()

                print(58)
                tto_.happen(self.event_id, self.id, -1, f"{score[0]}:{score[1]}")

                print(59)
                Utils.api("technical_time_out_started", "logic", period_count=period_count, time_out_id=tto_.id, event_id=self.event_id, period_id=self.id)

                print(60)
                rv.extend(event.show_paused_match_template(self.id))
                print(61)

            if check_time_out():

                print(62)
                self.pause()

                print(63)
                to_ = TimeOut()
                to_.save()

                print(64)
                to_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, f"{score[0]}:{score[1]}")
                to_.save()
                
                print(65)
                Utils.api("time_out_started", "logic", period_count=period_count, time_out_id=to_.id, event_id=self.event_id, team_id=self.left_team_id if data[1] == "0" else self.right_team_id, period_id=self.id)

                print(66)
                rv.extend(event.show_paused_match_template(self.id))

            if check_action():

                print(67)
                action_ = Action()
                action_.save()

                print(68)
                action_.happen(self.event_id, self.id, self.left_team_id if data[1] == "0" else self.right_team_id, int(data[2]), f"{score[0]}:{score[1]}")
                action_.save()

                print(69)
                Utils.api("action_happened", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, action_id=action_.id, team_id=self.left_team_id if data[1] == "0" else self.right_team_id, action_type=int(data[2]))

                print(70)
                rv.extend(event.show_match_template(self.id))

            if check_ball_control(): #TODO make new model (BallControlChange)

                print(71)
                self.ball_possesion_team_id = self.left_team_id if data[1] == "0" else self.right_team_id if data[1] == "2" else -1
                self.save()

                print(72)
                Utils.api("ball_possesion_changed", "logic", event_id=self.event_id, period_count=period_count, period_id=self.id, possession_index=int(data[1]))

                print(73)
                rv.extend(event.show_match_template(self.id))

            if check_show() or len(rv) == 0:
                
                print(74)
                if self.is_paused:
                    rv.extend(event.show_paused_match_template(self.id))
                else:
                    rv.extend(event.show_match_template(self.id))

            print(75) 
            return rv
        
        except Exception as e:
            print(e)

    def cancel(self): #TODO JSON
        pass