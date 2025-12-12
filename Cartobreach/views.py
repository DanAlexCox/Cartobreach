from django.shortcuts import render
from django import template
from . import tasks

#register library for templates
register = template.Library()

#handles form input and applies conditional rendering.
def check_age(request):
    age = None
    if request.method == 'POST':
        # request.POST.get returns a string, default to "0"
        age = int(request.POST.get('age', 0))
    return render(request, 'check_age.html', {'age': age})

#passes a list and string to demonstrate looping and filters.
def loop(request):
    data = "Gfg is the best"
    number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    context = {
        "data": data,
        "list": number_list
    }
    return render(request, "loop.html", context)

#returns variable type
@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__

valid_includes = ["map.html", "analysis.html", "filter.html"]
default_dates = ["01.01.2000", "01.01.2025"]

# index page dictionary function
def index(request):
    #default incident date range
    startStartDate = request.GET.get('startdate', '2000-01-01')
    endStartDate = request.GET.get('enddate', '2025-01-01')
    
    mapload = request.POST.get('mapload')
    if mapload not in valid_includes:
        mapload = None
    mapanalytics = request.POST.get('mapanalytics')
    if mapanalytics not in valid_includes:
        mapanalytics = None
    #content dictionary
    context = {
        'index' : "",
        'startdate' : startStartDate,
        'enddate' : endStartDate,
        'mapload' : mapload,
        'mapanalytics' : mapanalytics,
        'totalincidents' : tasks.totalIncidents,
        'corporateattacks' : tasks.corporateAttacks,
        'corporateattackspercent' : tasks.corporateAttacksPercent,
        'militaryattacks' : tasks.militaryAttacks,
        'militaryattackspercent' : tasks.militaryAttacksPercent,
    }
    return render(request, "index.html", context)

# function for filter form
def filter(request):
    # check if html made a post
    startStartDate = request.get('startdate', '2000-01-01')
    endStartDate = request.get('enddate', '2025-01-01')
    return 