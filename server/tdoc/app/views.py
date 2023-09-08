from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
    return render(request, 'testWebComponent.html');

def renderlatex(request):
    return HttpResponse('Hello Latex');
