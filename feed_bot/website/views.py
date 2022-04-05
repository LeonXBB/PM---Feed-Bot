from decouple import config

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@method_decorator(csrf_exempt, name="dispatch")
class Index(TemplateView):

    data = []

    server_address = config("server_address")
    requests_interval = config("server_ajax_update_interval")

    def get(self, request):
        return render(request, "index/index.html", context={"server_address": self.server_address, "requests_interval": self.requests_interval}) 
    
    def post(self, request):
        pass


@csrf_exempt
def index(request, data=[]):
    
    

    rv = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    </head>
    
    <body>
      <table>
        <tr>
            <th>
                ID
            </th>
            <th>
                Text
            </th>
        </tr>
    '''

    for i, data_piece in enumerate(data):
        rv += f'''
        <tr>
            <th>
                {data_piece["id"]}
            </th>
            <th>
                {data_piece["text"]}
            </th>
        </tr>
        '''

    rv += '''
      </table>
    </body>
    '''   
