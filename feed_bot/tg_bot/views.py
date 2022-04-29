from asyncio import sleep
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from decouple import config

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import time
import datetime

from .bin.utils import Utils
from . import models

# Create your views here.

@method_decorator(csrf_exempt, name="dispatch")
class BotAPI(TemplateView):

    def post(self, request): #TODO turn subfunctions from here into class methods (OR decorators!)
        
        null = None
        data = eval(request.body.decode("utf8"))

        task = data["task"]

        if task == "get":

            def init():

                if "order_by" not in list(data.keys()):
                    data["order_by"] = ["id",]

                obj_class = getattr(models, data["model"])
                query_set = list(obj_class.objects.all().order_by(*data["order_by"]))
                return obj_class, query_set
            
            def filter_set():
                
                rv = []
                for obj_instance in query_set:
                    
                    true = True

                    for k, v in data["params"].items():
                        if not getattr(obj_instance, k) == v:
                            true = False
                    
                    if true:
                        rv.append(list())
                        for field in data["fields"]:
                            rv[-1].append(getattr(obj_instance, field))

                return rv
            
            obj_class, query_set = init()

            if not len(query_set): rv = [0, ]
            else: rv = filter_set()    

            return JsonResponse(rv, safe=False)
        
        elif task == "get_fields":

            def init():

                if "order_by" not in list(data.keys()):
                    data["order_by"] = ["id",]

                obj_class = getattr(models, data["model"])
                return obj_class
            
            obj_class = init()

            rv = [str(x) for x in list(obj_class._meta.fields)]

            return JsonResponse(rv, safe=False)

        elif task == "get_all":

            def init():

                if "order_by" not in list(data.keys()):
                    data["order_by"] = ["id",]

                obj_class = getattr(models, data["model"])
                query_set = list(obj_class.objects.all().order_by(*data["order_by"]))
                return obj_class, query_set
            
            def filter_set():
                
                rv = []
                for obj_instance in query_set:
                                      
                    rv.append(list())
                    
                    if "fields" not in list(data.keys()):
                        data["fields"] =  [str(x).split(".")[-1] for x in list(obj_class._meta.fields)]
                    
                    for field in data["fields"]:
                        rv[-1].append(getattr(obj_instance, field))

                return rv
            
            obj_class, query_set = init()

            if not len(query_set): rv = [0, ]
            else: rv = filter_set()    

            return JsonResponse(rv, safe=False)

        elif task == "get_or_make":

            def init():

                if "order_by" not in list(data.keys()):
                    data["order_by"] = ["id",]

                obj_class = getattr(models, data["model"])
                query_set = list(obj_class.objects.all().order_by(*data["order_by"]))
                return obj_class, query_set
            
            def make_new(): # SEND WHAT YOU WANT TO SET (IF MAKE) IN PARAMS, WHAT YOU WANT TO RECEIVE (ANY CASE) IN FIELDS #TODO write proper documentation 
                
                rv = []
                
                if "id" in list(data["params"].keys()):
                    data["params"].pop("id")

                if getattr(obj_class, "created", None) is not None:
                    obj_instance = obj_class(**data["params"], created=str({"by": data['by'], "at": int(time.time())}))
                else:
                    obj_instance = obj_class(**data["params"])
                
                obj_instance.save()

                for field in data["fields"]:
                    rv.append(getattr(obj_instance, field))
                return [rv, ]

            def filter_set():
                
                rv = []
                for obj_instance in query_set:
                    
                    true = True

                    for k, v in data["params"].items():
                        if not getattr(obj_instance, k) == v:
                            true = False
                    
                    if true:
                        rv.append(list())
                        for field in data["fields"]:
                            rv[-1].append(getattr(obj_instance, field))            
                return rv
            
            obj_class, query_set = init()

            if not len(query_set) or not len(filter_set()): rv = make_new()
            else: rv = filter_set()

            return JsonResponse(rv, safe=False)

        elif task == "update":

            def init():

                if "order_by" not in list(data.keys()):
                    data["order_by"] = ["id",]

                obj_class = getattr(models, data["model"])
                query_set = list(obj_class.objects.all().order_by(*data["order_by"]))
                return obj_class, query_set

            def filter_set():
                
                rv = []
                for obj_instance in query_set:
                    
                    true = True

                    for k, v in data["filter_params"].items():
                        if not getattr(obj_instance, k) == v:
                            true = False
                    
                    if true:
                        rv.append(obj_instance)
            
                return rv

            def run_set():
                for obj_instance in query_set:
                    for k, v in data["update_params"].items():
                        setattr(obj_instance, k, v)
                    obj_instance.save()

                return [0, ]


            obj_class, query_set = init()
            query_set = filter_set()
            rv = run_set()

            return JsonResponse(rv, safe=False)

        elif task == "execute_method":

            def init():

                if "order_by" not in list(data.keys()):
                    data["order_by"] = ["id",]

                obj_class = getattr(models, data["model"])
                query_set = list(obj_class.objects.all().order_by(*data["order_by"]))
                return obj_class, query_set   

            def filter_set():
                
                rv = []
                for obj_instance in query_set:
                    
                    true = True

                    for k, v in data["params"].items():
                        if not getattr(obj_instance, k) == v:
                            true = False
                    
                    if true:
                        rv.append(obj_instance)
            
                return rv

            def run_set():

                rv = []

                if type(data["method"]["params"]) is list:       
                    for obj_instance in query_set:
                        rv.append(getattr(obj_instance, data["method"]["name"])(*data["method"]["params"]))

                elif type(data["method"]["params"]) is dict:   
                    for obj_instance in query_set:
                        rv.append(getattr(obj_instance, data["method"]["name"])(**data["method"]["params"]))

                else:
                    raise NotImplemented("If you only have one argument, please pack it into list or dict!")

                return rv

            obj_class, query_set = init()
            
            if data["params"] != "classmethod": 
                query_set = filter_set()
            else:
                query_set = [obj_class, ]
            
            rv = run_set()

            return JsonResponse(rv, safe=False)

        elif task == "kick_in":

            def google_sheets_magic(sheet_type):

                sleep_time = 1
                passed = False

                while not passed:
                    
                    try:
                        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
                        creds = ServiceAccountCredentials.from_json_keyfile_name("tg_bot/creds.json", scope)
                        client = gspread.authorize(creds)
                        sheet = client.open(config(sheet_type)).sheet1  # Open the spreadhseet

                        return sheet

                    except:
                        print("Error connecting to Google Sheets. Retrying in {} seconds...".format(sleep_time))
                        time.sleep(sleep_time)
                        sleep_time *= 2

            def init_localization():
                
                def init_text_languages():
                    
                    def init_text_language(language_index):
                        
                        print('here', language_index)

                        new_obj = models.TextLanguage()
                        
                        sleep_time = 1
                        passed = False

                        while not passed:

                            try:

                                if localziation_sheet.cell(4, language_index).value:
                                    new_obj.self_name = localziation_sheet.cell(4, language_index).value
                                passed = True 

                            except:

                                print(f"Hit Google API limit while downloading languages, point {language_index-2} / 5, sleeping for {sleep_time} seconds...") #TODO change to logger
                                time.sleep(sleep_time)
                                sleep_time *= 2

                        new_obj.save()

                    models.TextLanguage.objects.all().delete()

                    for i in range(3, 8):
                        init_text_language(i)

                def init_text_strings():
                    
                    def init_text_string(string_index):
                        
                        new_obj = models.TextString()

                        sleep_time = 1
                        passed = False

                        while not passed:

                            try:
                                
                                for i in range(1,8):
                                    if localziation_sheet.cell(string_index, i).value:
                                        setattr(new_obj, localziation_sheet.cell(3, i).value, localziation_sheet.cell(string_index, i).value)

                                passed = True
                            
                            except:
                                print(f"Hit Google API limit while downloading text strings, point {string_index-5}, sleeping for {sleep_time} seconds...")
                                time.sleep(sleep_time)
                                sleep_time *= 2

                        new_obj.save()

                    models.TextString.objects.all().delete()

                    for i in range(5, len(localziation_sheet.get_all_values())):
                        init_text_string(i)

                init_text_languages()
                init_text_strings()

            def init_rules_sets():

                def init_rule_set(sheet_col_index):
                    
                    new_obj = models.RulesSet()

                    for i in range(1, params_count+1):
                        
                        sleep_time = 1
                        passed = False
                        
                        while not passed:
                            try:
                                if rules_sets_sheet.cell(i, 1) and rules_sets_sheet.cell(i, 1).value:
                                    
                                    setattr(new_obj, rules_sets_sheet.cell(i, 1).value.split("\n")[0], rules_sets_sheet.cell(i, sheet_col_index).value)

                                passed = True

                            except:
                                print(f"Hit Google API limit while downloading rules sets, point {i} / {params_count}, sleeping for {sleep_time} seconds...") #TODO change to logger
                                time.sleep(sleep_time)
                                sleep_time *= 2

                    new_obj.save()

                models.RulesSet.objects.all().delete()

                rules_sets_count = len(rules_sets_sheet.get_all_values()[0]) - 1
                params_count = len(rules_sets_sheet.get_all_values())
                for i in range(2, rules_sets_count+2):
                    init_rule_set(i)

            #localziation_sheet = google_sheets_magic("localization_table_name")
            #rules_sets_sheet = google_sheets_magic("rules_sets_schema_table_name")
            
            #init_localization()
            #init_rules_sets()

            Utils.init_screens("server")

            return JsonResponse([0, ], safe=False)

@method_decorator(csrf_exempt, name="dispatch")
class BotLogicAPI(TemplateView): # TODO

    channel_layer = get_channel_layer()

    def post(self, request):

        from .models import Event, Team, RulesSet, TimeOut, Period
        from website.models import APIMessage

        data = eval(request.body.decode("utf8"))

        task = data["task"]

        if task == "event_template_created":
            
            event = Event.objects.get(id=data["event_id"])

            string = f"Подія {data['event_id']} створена"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "event_template_updated":
            
            def get_verbose_vals():

                old_val = data["old_val"]
                new_val = data["new_val"]
                                
                if data["attr"] == "home_team":
                    try: #TODO change to check if team exists
                        old_val = getattr(models, "Team")._get_({"id": data["old_val"]})[0].name
                    except:
                        old_val = ""
                    
                    new_val = getattr(models, "Team")._get_({"id": data["new_val"]})[0].name
                
                elif data["attr"] == "away_team":
                    try: #TODO change to check if team exists
                        old_val = getattr(models, "Team")._get_({"id": data["old_val"]})[0].name
                    except:
                        old_val = ""

                    new_val = getattr(models, "Team")._get_({"id": data["new_val"]})[0].name
                
                elif data["attr"] == "competition":                
                    
                    try: #TODO change to check if competition exists
                        old_val = getattr(models, "Competition")._get_({"id": data["old_val"]})[0].name
                    except:
                        old_val = ""
                    
                    new_val = getattr(models, "Competition")._get_({"id": data["new_val"]})[0].name
                
                elif data["attr"] == "rules_set":
                    
                    try: #TODO change to check if rules_set exists
                        old_val = getattr(models, "RulesSet")._get_({"id": data["old_val"]})[0].name
                    except:
                        old_val = ""

                    new_val = getattr(models, "RulesSet")._get_({"id": data["new_val"]})[0].name

                return old_val, new_val

            old_val, new_val = get_verbose_vals()

            string = f"Подія {data['event_id']} оновлена, параметр {data['attr']} змінено з {old_val} на {new_val}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "event_scheduled":

            datetime_string = datetime.datetime.fromtimestamp(data["event_epoch"], None)

            event = Event._get_({'id': data["event_id"]})[0]

            string = f"Подія {event.id} запланована на {datetime_string}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

            async_to_sync(self.channel_layer.group_send)(
                f"events_list_{event.rules_set_id}",
                {"type": "append.new.event", "content": event.id}
            )

        elif task == "event_started":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Подія {data['event_id']} почалася"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "event_ended":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Подія {data['event_id']} завершена"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "event_cancelled":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Подія {data['event_id']} скасована"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "period_scheduled":
            
            datetime_string = datetime.datetime.fromtimestamp(data["period_epoch"], None)

            event = Event._get_({'id': data["event_id"]})[0]

            string = f"Період {data['period_count']} ({data['period_id']}) події {data['event_id']} запланований на {datetime_string}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "period_started":

            event = Event._get_({'id': data["event_id"]})[0]

            string = f"Період {data['period_count']} ({data['period_id']}) події {data['event_id']} почався"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "period_ended":

            event = Event._get_({'id': data["event_id"]})[0]

            string = f"Період {data['period_count']} ({data['period_id']}) події {data['event_id']} завершений"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "action_happened":

            team_name = Team._get_({"id": data["team_id"]})[0].name
            event = Event._get_({"id": data["event_id"]})[0]
            action_name = RulesSet._get_({"id": event.rules_set_id})[0].actions_list[data["action_type"]]

            string = f"Дія {action_name} ({data['action_id']}) команди {team_name}, період {data['period_count']} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "action_cancelled":
            pass

        elif task == "coin_toss_scheduled":

            event = Event._get_({'id': data["event_id"]})[0]
            datetime_string = datetime.datetime.fromtimestamp(data["coin_toss_epoch"], None)

            string = f"Жеребкування # {data['coin_toss_count'] + 1} перед періодом {data['period_count'] + 1} події {data['event_id']} заплановано на {datetime_string}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "coin_toss_started":
            
            string = f"Жеребкування # {data['coin_toss_count'] + 1} ({data['coin_toss_id']}) перед періодом {data['period_count'] + 1} події {data['event_id']} почалося"
            mess = APIMessage()
            mess.add(data["event_id"], string)
            mess.send()

        elif task == "coin_toss_edited":

            attr = "Команда зліва" if data["attr"] == "left_team_id" else "Команда, що починає"
            val = data["val"]

            try:
                val = Team._get_({"id": data["val"]})[0].name
            except:
                val = ""

            string = f"Жеребкування # {data['coin_toss_count']} ({data['coin_toss_id']}) перед періодом {data['period_count'] + 1} події {data['event_id']}: нове значення параметру {attr}: {val}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "coin_toss_saved":
            
            event = Event._get_({"id": data["event_id"]})[0]

            left_team_name = Team._get_({"id": data["left_team_id"]})[0].name
            ball_possession_team_name = Team._get_({"id": data["ball_possession_team_id"]})[0].name

            string = f"Жеребкування # {data['coin_toss_count']} ({data['coin_toss_id']}) перед періодом {data['period_count']} ({data['period_id']}) події {data['event_id']} підтверджено. Команда зліва: {left_team_name}. Команда, що починає: {ball_possession_team_name}."
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "coin_toss_start_cancelled":
            pass

        elif task == "coin_toss_edit_cancelled":
            pass

        elif task == "coin_toss_save_cancelled":
            pass

        elif task == "point_happened":

            event = Event._get_({"id": data["event_id"]})[0]
            team_name = Team._get_({"id": data["team_id"]})[0].name
            point_type_name = RulesSet._get_({"id": event.rules_set_id})[0].scores_names[data["point_type"]]

            async_to_sync(self.channel_layer.group_send)(
                f'event_data_{event.id}',
                {"type": "update.scores", "content_team": 0 if data["team_id"] == event.home_team_id else 1, "content_period": data["period_count"]-1, "content_value": data["point_value"], "content_opposite_value": data["opposite_point_value"], "content_score": data["new_team_score"], "content_opposite_score": data["new_opposite_team_score"]}
            )

            string = f"Зміна рахунку команди {team_name}. Тип: {point_type_name}, вага: {data['point_value']}, вага протилежної команди: {data['opposite_point_value']}, нове значення рахунку: {data['new_team_score']}, протилежної команди: {data['opposite_team_score']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "point_cancelled":
            pass

        elif task == "side_change_after_period_happened":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Зміна сторін ({data['side_change_id']}) піcля періоду {data['period_count']} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "side_change_after_period_cancelled":
            pass

        elif task == "side_change_during_period_happened":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Зміна сторін ({data['side_change_id']}) під час періоду {data['period_count']} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "side_change_during_period_cancelled":
            pass

        elif task == "technical_time_out_started":
            
            event = Event._get_({"id": data["event_id"]})[0]

            technical_time_out_count = len(TimeOut._get_({"event_id": data["event_id"], "period_id": data["period_id"], "is_technical": 1}))

            string = f"Почався {technical_time_out_count}-й технічний тайм-аут ({data['time_out_id']}) в періоду {data['period_count']} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "technical_time_out_ended":
            
            event = Event._get_({"id": data["event_id"]})[0]

            technical_time_out_count = len(TimeOut._get_({"event_id": data["event_id"], "period_id": data["period_id"], "is_technical": 1}))

            string = f"Закінчився {technical_time_out_count}-й технічний тайм-аут ({data['time_out_id']}) в періоду {data['period_count']} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "technical_time_out_cancelled":
            pass

        elif task == "time_out_started":

            event = Event._get_({"id": data["event_id"]})[0]

            time_out_count = len(TimeOut._get_({"event_id": data["event_id"], "period_id": data["period_id"], "team_id": data["team_id"]}))
            team_name = Team._get_({"id": data["team_id"]})[0].name

            string = f"Почався {time_out_count}-й тайм-аут ({data['time_out_id']}) команди {team_name} ({data['team_id']}) в періоду {data['period_count']} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "time_out_ended":
            
            event = Event._get_({"id": data["event_id"]})[0]

            time_out_count = len(TimeOut._get_({"event_id": data["event_id"], "period_id": data["period_id"], "team_id": data["team_id"]}))
            team_name = Team._get_({"id": data["team_id"]})[0].name

            period_count = len(Period._get_({"id": data["period_id"]}))

            string = f"Закінчився {time_out_count}-й тайм-аут ({data['time_out_id']}) команди {team_name} ({data['team_id']}) в періоду {period_count} ({data['period_id']}) події {data['event_id']}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "time_out_cancelled":
            pass

        elif task == "period_paused":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Подія {data['event_id']}, період {data['period_count']} ({data['period_id']}) призупинена"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "period_resumed":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Подія {data['event_id']}, період {data['period_count']} ({data['period_id']}) поновлена"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        elif task == "ball_possesion_changed":

            event = Event._get_({"id": data["event_id"]})[0]

            string = f"Подія {data['event_id']}, період {data['period_count']} ({data['period_id']}), перехід контролю м'яча: м'яч {'лівої команди' if data['possession_index'] == 0 else 'правої команди' if data['possession_index'] == 2 else 'нічій'}"
            mess = APIMessage()
            mess.add(event.id, string)
            mess.send()

        return JsonResponse(data, safe=False)
