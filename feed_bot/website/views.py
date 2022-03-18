from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json

# Create your views here.

@method_decorator(csrf_exempt, name="dispatch")
class Index(TemplateView):

    data = []

    def get(self, request):
        return render(request, "index.html") 
    
    def post(self, request):
        if request.POST["task"] == "update":
            self.data.append({"id": request.POST["id"], "text": request.POST["text"]})
            return HttpResponse(request, "", status=200)
        elif request.POST["task"] == "get":
            return JsonResponse(self.data, safe=False)


@csrf_exempt
def index(request, data=[]):
    if request.method == "POST":
        data.append({"id": request.POST["id"], "text": request.POST["text"]})

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
        print(data_piece)
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

    return HttpResponse(rv)
    
