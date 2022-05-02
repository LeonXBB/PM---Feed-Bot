from decouple import config

from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse

import time

@method_decorator(csrf_exempt, name="dispatch")
class Index(TemplateView):

    def get(self, request):
        print('\n', time.strftime("%H:%M:%S"), 'received get request, trying to reply...')
        try:
            return render(request, "index/index.html", {"server_address": config("server_address")}, status=200)
        except Exception as e:
            print('\n', time.strftime("%H:%M:%S"), 'error occured:', e)

    def post(self, request):
        pass

class Ping(TemplateView):

    def get(self, request):
        print('\n', time.strftime("%H:%M:%S"), 'received ping request, trying to reply...')
        try:
            return HttpResponse(status=200)
        except Exception as e:
            print('\n', time.strftime("%H:%M:%S"), 'error occured:', e)