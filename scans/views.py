from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    latest_question_list = Question.objects.all().order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def main(request):
    return HttpResponse("Hello, world. You're at the scans index.")

def plots(request, beamline):
    return HttpResponse("You're looking at scan data from  %s." % beamline)

def images(request, beamline):
    response = "You're looking at scan images from %s."
    return HttpResponse(response % beamline)

