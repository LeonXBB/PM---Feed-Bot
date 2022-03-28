from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import time

from .bin.utils import Utils
from . import models
from .screens.Screen import Screen

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
                query_set = list(obj_class.objects.all().order_by(*data["order_by"]))
                return obj_class, query_set
            
            obj_class, wrong_rv = init()

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
                    obj_instance = obj_class(**data["params"], created=f"{data['by']};{int(time.time())}")
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
            query_set = filter_set()
            rv = run_set()

            return JsonResponse(rv, safe=False)

        elif task == "kick_in":
            
            Utils.init_screens("server")

            return JsonResponse([0, ], safe=False)

@method_decorator(csrf_exempt, name="dispatch")
class BotLogicAPI(TemplateView): # TODO

    def post(self, request):
        
        data = eval(request.body.decode("utf8"))

        print(f"DATA //// /// // /{data}")
       
        return JsonResponse(data, safe=False)
