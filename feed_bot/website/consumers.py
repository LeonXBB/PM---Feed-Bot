from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer

import json

class RulesSetConsumer(WebsocketConsumer):
    
    def connect(self):
        
        self.accept()

        from tg_bot.models import RulesSet


        mess = []

        for rules_set in list(RulesSet.objects.all()):
            mess.extend((rules_set.id, rules_set.name))

        self.send(json.dumps(mess))

class EventsListConsumer(WebsocketConsumer):

    def connect(self): #TODO write disconnect function
        self.accept()

    def receive(self, text_data=None, bytes_data=None):

        if text_data.startswith("rules_set_id"): #TODO check for multiple rules set ids at the same time
            rules_set_id = text_data.split("=")[1]
            async_to_sync(self.channel_layer.group_add)(f'events_list_{rules_set_id}', self.channel_name)

        from tg_bot.models import Event, Competition, Team

        mess = []

        for event in list(Event._get_({"rules_set_id": int(rules_set_id)})):

            comp_name = Competition._get_({'id': event.competition_id})[0].name
            home_team_name = Team._get_({'id': event.home_team_id})[0].name
            away_team_name = Team._get_({'id': event.away_team_id})[0].name
            is_live = 1 if event.status == 2 else 0

            mess.extend((event.date_scheduled, event.time_scheduled, event.id, comp_name, home_team_name, away_team_name, is_live))

        self.send(text_data=json.dumps(mess))

    def append_new_event(self, channel_event):
        
        from tg_bot.models import Event, Competition, Team

        event = Event._get_({'id': channel_event.get("content")})[0]

        comp_name = Competition._get_({'id': event.competition_id})[0].name
        home_team_name = Team._get_({'id': event.home_team_id})[0].name
        away_team_name = Team._get_({'id': event.away_team_id})[0].name    

        mess = [event.date_scheduled, event.time_scheduled, event.id, comp_name, home_team_name, away_team_name, 0, "append"]

        self.send(text_data=json.dumps(mess))

class EventConsumer(WebsocketConsumer):
    
    def connect(self):

        self.accept()

    def receive(self, text_data=None, bytes_data=None):

        def get_period_score(period_number):
            
            score = [0, 0]
            periods = [period_id for period_id in event.periods_ids.split(";") if period_id]

            try:
                    
                period_id = periods[period_number]
                period = Period._get_({'id': int(period_id)})[0]

                for point_id in period.points_ids.split(";"):
                    if point_id:
                        point = Point._get_({'id': int(point_id)})[0]
                        if point.team_id == event.home_team_id:
                            score[0] += point.value
                        else:
                            score[1] += point.value
            except Exception as e:
                pass

            return score

        if text_data.startswith("event_id"): #TODO check for multiple events at the same time
            event_id = text_data.split("=")[1]
            async_to_sync(self.channel_layer.group_add)(f'event_data_{event_id}', self.channel_name)
    
        from tg_bot.models import Event, Period, Point, Team, RulesSet
        from website.models import APIMessage

        event = Event._get_({'id': int(event_id)})[0]

        home_team_name = Team._get_({'id': event.home_team_id})[0].name
        away_team_name = Team._get_({'id': event.away_team_id})[0].name
    
        periods_in_event = RulesSet._get_({'id': event.rules_set_id})[0].periods_in_event

        mess = [periods_in_event, ]

        total = [0, 0]
        for i in range(periods_in_event):
            scores = get_period_score(i)
            total[0] += scores[0]
            total[1] += scores[1]
            mess.extend(scores)

        mess.extend((home_team_name, away_team_name, len(list(period_id for period_id in event.periods_ids.split(";") if period_id)), total[0], total[1]))

        try:
            mess.append("messages_start")

            for message in APIMessage.objects.filter(event_id=int(event_id)):
                mess.extend((f"{message.hour}:{message.minute}:{message.second}", f"{message.score_1}:{message.score_2}", message.message))

            mess.append("messages_end")
        except Exception as e:
            print(e)

        self.send(text_data=json.dumps(mess))

    def update_messages(self, channel_event):

        mess = f"new_message_{channel_event.get('time')}_{channel_event.get('scores')}_{channel_event.get('message')}"

        self.send(text_data=json.dumps(mess))

    def update_scores(self, channel_event):

        mess = f"new_score_{channel_event.get('content_team')}_{channel_event.get('content_period')}_{channel_event.get('content_value')}_{channel_event.get('content_score')}"

        self.send(text_data=json.dumps(mess))

    def update_stats(self, channel_event):
        pass