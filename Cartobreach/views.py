from django.shortcuts import render
from django.utils.safestring import mark_safe
from django import template
from datetime import datetime
from . import tasks
from . import dataset
from . import continents
from . import countries

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
    svg = continents.renderContinentMap()
    # replace function not working
    # svg = svg.replace("xlink:href", "href")
    mapSvg = mark_safe(svg)
    # get selected continent object
    # filters dataset based on selected continent
    dataset.df["receiver_country_alpha_2_code"] = dataset.cleanColumn(dataset.df["receiver_country_alpha_2_code"])
    dataset.df["receiver_continent_code"] = dataset.df["receiver_country_alpha_2_code"].apply(dataset.convertCountryCodeToContinentCode)
    dataset.df["receiver_continent_code"] = dataset.df["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    getContinent = request.GET.get('continent') # load GET continent (value should be .getName())
    selected = None
    for i in continents.continentList: 
        if i.getName() == getContinent:
            selected = i
            contSet = dataset.filterSpecificColumn(dataset.df, dataset.df["receiver_continent_code"], selected.getAlphaCode())
            # analytics of a continent
            totalContinent = len(contSet.index) # total continent incidents
            totalContinentPercent = round((float(totalContinent)/float(len(dataset.df.index)) * 100), 2) # percentage of total incidents in continent
            corpContinentAttacks = dataset.countUncleanColumnValues(contSet["receiver_category"], "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)") # total corporate attacks in continent
            corpContinentAttacksPercent = round((float(corpContinentAttacks)/float(totalContinent)) * 100, 2) # corporate continent attack percentage
            miliContinentAttacks = dataset.countUncleanColumnValues(contSet["receiver_subcategory"], "Military") # military received attacks in continent
            miliContinentAttacksPercent = round((float(miliContinentAttacks)/float(totalContinent)) * 100, 2) # military continent attack percentage
            inciContSet = dataset.cleanColumn(contSet["incident_type"]) # clean incident type column of continent dataset
            continentAttackTypePiechart = dataset.pieChart(inciContSet) # make pie chart of incident type in continent
            continentAttackTypePieSvg = mark_safe(continentAttackTypePiechart)
            break
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
        'map' : mapSvg,
        'continentlist' : continents.continentList,
    }
    if selected != None:
        context.update({
            'continent' : getContinent,
            'continenttotal' : totalContinent,
            'continenttotalpercent' : totalContinentPercent,
            'continentcorporate' : corpContinentAttacks,
            'continentcorporatepercent' : corpContinentAttacksPercent,
            'continentmilitary' : miliContinentAttacks,
            'continentmilitarypercent' : miliContinentAttacksPercent,
            'continentattacktypesvg' : continentAttackTypePieSvg,
        })
            
    return render(request, "index.html", context)
