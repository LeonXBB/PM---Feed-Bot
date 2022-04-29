from decouple import config

from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name="dispatch")
class Index(TemplateView):

    def get(self, request):
        return render(request, "index/index.html", {"server_address": config("server_address")}, status=200)
    
    def post(self, request):
        pass