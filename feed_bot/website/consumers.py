from cgitb import text
from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer

import json

class RulesSetConsumer(WebsocketConsumer):
    
    def connect(self):

        from tg_bot.models import RulesSet

        self.accept()

        mess = []

        for rules_set in list(RulesSet.objects.all()):
            mess.extend((rules_set.id, rules_set.name))

        self.send(json.dumps(mess))


class EventsListConsumer(WebsocketConsumer):

    def connect(self):

        from tg_bot.models import RulesSet

        for rules_set in list(RulesSet.objects.all()):
            async_to_sync(self.channel_layer.group_add)(f'events_list_{rules_set.id}', self.channel_name)

        self.accept()

    def disconnect(self, code): #TODO write disconnect method
        pass

    def receive(self, text_data=None, bytes_data=None):

        from tg_bot.models import Event, Competition, Team

        mess = []

        for event in list(Event._get_({"rules_set_id": int(text_data)})):

            comp_name = Competition._get_({'id': event.competition_id})[0].name
            home_team_name = Team._get_({'id': event.home_team_id})[0].name
            away_team_name = Team._get_({'id': event.away_team_id})[0].name
            is_live = 1 if event.status == 2 else 0

            mess.extend((event.date_scheduled, event.time_scheduled, event.id, comp_name, home_team_name, away_team_name, is_live))

        self.send(text_data=json.dumps(mess))

    def append_new_event(self, event_id):
        
        event_id = event_id.get("content")

        from tg_bot.models import Event, Competition, Team

        event = Event._get_({'id': event_id})[0]

        comp_name = Competition._get_({'id': event.competition_id})[0].name
        home_team_name = Team._get_({'id': event.home_team_id})[0].name
        away_team_name = Team._get_({'id': event.away_team_id})[0].name    

        mess = [event.date_scheduled, event.time_scheduled, event.id, comp_name, home_team_name, away_team_name, 0, "append"]

        self.send(text_data=json.dumps(mess))

        '''
        async_to_sync(self.channel_layer.group_send)(f'events_list_{event.rules_set_id}', {
            'type': 'send',
            'content': json.dumps(mess)
        })
        '''

class EventConsumer(WebsocketConsumer):
    pass