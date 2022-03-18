from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json

from . import models
# Create your views here.

@method_decorator(csrf_exempt, name="dispatch")
class BotAPI(TemplateView):

    def post(self, request): #TODO turn subfunctions from here into class methods

        data = eval(request.body.decode("utf-8"))

        task = data["task"]

        if task == "get":

            def init():
                return getattr(models, data["class"]), list(getattr(models, data["class"]).objects.all())
            
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

            if not len(query_set): rv = None
            else: rv = filter_set()    

            return JsonResponse(rv, safe=False)
        
        elif task == "get_or_make":

            def init():
                return getattr(models, data["class"]), list(getattr(models, data["class"]).objects.all())
            
            def make_new():
                
                rv = []
                
                obj_instance = obj_class(**data["params"])
                obj_instance.save()

                for field in data["fields"]:
                    rv.append(getattr(obj_instance, field))
                return rv

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

            if not len(query_set): rv = make_new()
            else: rv = filter_set()    

            return JsonResponse(rv, safe=False)

        elif task == "execute_method":

            def init():
                return getattr(models, data["class"]), list(getattr(models, data["class"]).objects.all())            

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
