from django.shortcuts import render
from django import template
from datetime import datetime
from . import tasks
from . import dataset

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
    minDate = datetime.strptime(request.GET.get('startdate', '2000-01-01'), '%Y-%m-%d')
    maxDate = datetime.strptime(request.GET.get('enddate', '2025-01-01'), '%Y-%m-%d')
    # filter dataset
    ds = tasks.filterDatasetByDate(minDate.strftime('%d.%m.%Y'), maxDate.strftime('%d.%m.%Y'))
    # filter variables from tasks.py
    totalIncidents = len(ds.index) # total incidents in date range
    print(totalIncidents)
    corporateAttacks = dataset.countUncleanColumnValues(ds["receiver_category"], "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)") # total corporate attacks in date range
    corporateAttacksPercent = round((float(corporateAttacks) / float(totalIncidents)) * 100, 2) # corporate attacks percentage in date range
    militaryAttacks = dataset.countUncleanColumnValues(ds["receiver_subcategory"],"Military") # military attacks in date range
    militaryAttacksPercent = round((float(militaryAttacks) / float(totalIncidents)) * 100, 2) # military attacks percentage in range
    
    # check map button has been clicked
    mapload = request.POST.get('mapload')
    if mapload not in valid_includes:
        mapload = None
    # check analytics button has been clicked
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
        'totalincidents' : totalIncidents,
        'corporateattacks' : corporateAttacks,
        'corporateattackspercent' : corporateAttacksPercent,
        'militaryattacks' : militaryAttacks,
        'militaryattackspercent' : militaryAttacksPercent,
    }
    return render(request, "index.html", context)