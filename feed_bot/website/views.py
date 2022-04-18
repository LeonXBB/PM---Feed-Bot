from decouple import config

from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@method_decorator(csrf_exempt, name="dispatch")
class Index(TemplateView):

    def get(self, request):

        return render(request, "index/index.html", {"server_address": config("server_address")})
    
    def post(self, request):
        pass