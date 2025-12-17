from django.shortcuts import render
from django import template
from datetime import datetime
from . import tasks
from . import dataset
from . import continents

#register library for templates
register = template.Library()

#returns variable type
@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__

valid_includes = ["map.html", "analysis.html", "filter.html"]

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
    # make new column receiver_continent with unique values only
    ds["receiver_country_alpha_2_code"] = dataset.cleanColumn(ds["receiver_country_alpha_2_code"])
    ds["receiver_continent_code"] = ds["receiver_country_alpha_2_code"].apply(dataset.convertCountryCodeToContinentCode)
    ds["receiver_continent_code"] = ds["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    # set total incident values for continents
    for continent in continents.continentList:
        continentSet = dataset.filterSpecificColumn(ds, ds["receiver_continent_code"], continent.getAlphaCode()) # filter date filted range for each continent
        continent.setValue(len(continentSet.index)) # total incidents in continent
    # load continents map
    continents.renderContinentMap(request)
    
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
