from django.shortcuts import render
from django.utils.safestring import mark_safe
from django import template
from django.http import JsonResponse
from datetime import datetime
from . import dataset
from . import continents
from . import countries
from .countries import countryList
from . import categories 

#register library for templates
register = template.Library()

#returns variable type
@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__

valid_includes = ["map.html", "analysis.html", "filter.html"]

# index page dictionary function
def index(request):
    # template requests
        # get region switch info (default to continents if not known) OPTIONAL: handle url editting errors
    selectRegion = request.GET.get('region', None) # on or None
    # selectGroup = request.GET.get('group') # on or None
    startStartDate = request.GET.get('startdate', '2020-01-01')
    endStartDate = request.GET.get('enddate', '2025-01-01')
    selectedReceiverCat = request.GET.getlist("receivertype")
    selectedReceiverSubCat = request.GET.getlist("receiversubtype")
    mapanalytics = request.POST.get('mapanalytics')
    mapload = None
    
    # make select dictionary
    selectDict = {}
    selectDict['switchregion'] = selectRegion
    # selectDict['switchgroup'] = selectGroup
    selectDict['filterstartdate'] = startStartDate
    selectDict['filterenddate'] = endStartDate
    selectDict['filterreceivercategorylist'] = selectedReceiverCat
    selectDict['filterreceiversubcategorylist'] = selectedReceiverSubCat
    
        # condition requests
    if selectRegion == None:
        getContinent = request.GET.get('continent') # load GET continent (value should be .getName())
        selectDict['receivercontinent'] = getContinent # dictionary add
    elif selectRegion == 'on':
        getCountry = request.GET.get('country') # load GET continent (value should be .getName())
        selectDict['receivercountry'] = getCountry # dictionary add
    else:
        getContinent = None
    
    if mapanalytics not in valid_includes:
        mapload = request.POST.get('mapload', 'map.html')
    
    
    # change start and enddate to string in d.m.y format
    minDate = datetime.strptime(startStartDate, '%Y-%m-%d')
    maxDate = datetime.strptime(endStartDate, '%Y-%m-%d')
    filterStartDate = datetime.strftime(minDate, '%d.%m.%Y')
    filterEndDate = datetime.strftime(maxDate, '%d.%m.%Y')# change start and end date to datetime
    
    # filter dataset using start and end date
    ds = dataset.filterDateRange(dataset.df, dataset.df["start_date"], minDate.strftime('%d.%m.%Y'), maxDate.strftime('%d.%m.%Y'))
    # TASK: check what group is selected
    receiverCatList = [] # get receiver category options
    receiverSubCat = {} # create dictionary for receiver categories with their subcategories
    for receiverCat in categories.receiverList:
        receiverCatList.append(receiverCat.getCatType())
        receiverSubCat[receiverCat.getCatType()] = receiverCat.getCatSubType()

    # filter dataset ds using selected receiver categories
    for recCat in selectedReceiverCat:
        ds = dataset.filterSpecificColumn(ds, ds["receiver_category"], recCat)
        
    # check if receiverSubCatFull contains values
    if selectedReceiverSubCat:
        # filter dataset ds using selected receiver subcategories
        for recSubCat in selectedReceiverSubCat:
            ds = dataset.filterSpecificColumn(ds, ds["receiver_subcategory"], recSubCat)
        
    # filter variables from tasks.py
    totalIncidents = len(ds.index) # total incidents in date range
    # TASK: update to include all/most critical infrastructure
    corporateAttacks = dataset.countUncleanColumnValues(ds["receiver_category"], "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)") # total corporate attacks in date range
    corporateAttacksPercent = round((float(corporateAttacks) / float(totalIncidents)) * 100, 2) # corporate attacks percentage in date range
   
    if mapanalytics not in valid_includes:
        mapanalytics = None
        
    # make new column receiver_continent with unique values only
    ds["receiver_country_alpha_2_code"] = dataset.cleanColumn(ds["receiver_country_alpha_2_code"])
    ds["receiver_continent_code"] = ds["receiver_country_alpha_2_code"].apply(dataset.convertCountryCodeToContinentCode)
    ds["receiver_continent_code"] = ds["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    
    # get current full url path for adding specific region onto it
    full_url = request.get_full_path()
    
    # check what region is selected, change between continents (default: None) and countries (on)
    if selectRegion == None:
        # set total incident values for continents
        for continent in continents.continentList:
            continentSet = dataset.filterSpecificColumn(ds, ds["receiver_continent_code"], continent.getAlphaCode()) # filter date filted range for each continent
            continent.setValue(len(continentSet.index)) # total incidents in continent
        # load continents map
        svg = continents.renderContinentMap()
    elif selectRegion == 'on':
        # set total incident values for each country
        for country in countries.countryList:
            countrySet = dataset.filterSpecificColumn(ds, ds["receiver_country_alpha_2_code"], country.getAlphaCodeUp())
            country.setValue(len(countrySet.index))
        # load countrys map
        svg = countries.renderCountryMap(totalIncidents, full_url)
    else:
        # set total incident values for continents
        for continent in continents.continentList:
            continentSet = dataset.filterSpecificColumn(ds, ds["receiver_continent_code"], continent.getAlphaCode()) # filter date filted range for each continent
            continent.setValue(len(continentSet.index)) # total incidents in continent
        # load continents map
        svg = continents.renderContinentMap()
    # replace function not working
    # svg = svg.replace("xlink:href", "href")
    mapSvg = mark_safe(svg)
    # Render graphs
    totalIncidentSvg = mark_safe(dataset.yearlyIncidentBarPlot(ds, filterStartDate, filterEndDate))
    monthlyIncidentSvg = mark_safe(dataset.monthlyAllAreasIncidentLinePlot(ds, ds["receiver_continent_code"], filterStartDate, filterEndDate))
    # TASK: determine check index switches i.e. region/group
        # construct dictionary for data analytics and svgs
    selected = None
    dataList = {}
    svgList = {}
    if selectRegion == None:
        for i in continents.continentList: 
            if i.getName() == getContinent:
                selected = i
                selectDict['selectcontinent'] = selected
                # filters dataset based on selected continent
                contSet = dataset.filterSpecificColumn(ds, ds["receiver_continent_code"], selected.getAlphaCode())
                # analytics of a continent
                totalContinent = len(contSet.index) # total continent incidents
                totalContinentPercent = round((float(totalContinent)/float(len(dataset.df.index)) * 100), 2) # percentage of total incidents in continent
                corpContinentAttacks = dataset.countUncleanColumnValues(contSet["receiver_category"], "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)") # total corporate attacks in continent
                corpContinentAttacksPercent = round((float(corpContinentAttacks)/float(totalContinent)) * 100, 2) # corporate continent attack percentage
                inciContSet = dataset.cleanColumn(contSet["incident_type"]) # clean incident type column of continent dataset
                continentAttackTypePieChart = dataset.pieChart(inciContSet) # make pie chart of incident type in continent
                continentAttackTypePieSvg = mark_safe(continentAttackTypePieChart)
                # make attacker continent code and pie chart
                contSet["initiator_alpha_2"] = dataset.cleanColumn(contSet["initiator_alpha_2"])
                contSet["initiator_continent_code"] = contSet["initiator_alpha_2"].apply(dataset.convertCountryCodeToContinentCode)
                contSet["initiator_continent_code"] = contSet["initiator_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
                continentAttackerLocationPieChart = dataset.pieChart(contSet["initiator_continent_code"])
                continentAttackerLocationPieSvg = mark_safe(continentAttackerLocationPieChart)
                # mitre initial access
                mitreAccessContSet = dataset.cleanColumn(contSet["mitre_initial_access"]) # clean incident type column of continent dataset
                continentMitreAccessPieChart = dataset.pieChart(mitreAccessContSet) # make pie chart of incident type in continent
                continentMitreAccessPieSvg = mark_safe(continentMitreAccessPieChart)
                # total weighted intensity of continent
                contSet["weighted_intensity"] = dataset.pd.to_numeric(contSet["weighted_intensity"], errors="coerce") # no need to call dataset.totalAreaIntensity, contSet is filtered and cleaned
                continentTotalIntensity = contSet["weighted_intensity"].sum()
                # mitre impact bar chart
                mitreImpactContSet = dataset.cleanColumn(contSet["mitre_impact"]) # clean mitre impacts for continent dataset
                continentMitreImpactBarChart = dataset.barChart(mitreImpactContSet) # make bar chart of mitre impact methods in continent
                continentMitreImpactBarChart = mark_safe(continentMitreImpactBarChart)
                break
    elif selectRegion == 'on':
        print('country selected')
    else:
        print('invalid input')

    #content dictionary
    context = {
        'index' : "",
        'aboutus' : "aboutus/",
        'sources' : "sources/",
        'startdate' : selectDict['filterstartdate'],
        'enddate' : selectDict['filterenddate'],
        'selectedreceivercats' : selectDict['filterreceivercategorylist'],
        'selectedreceiversubcats' : selectDict['filterreceiversubcategorylist'],
        'switchregion' : selectDict['switchregion'],
        'receivercatlist' : receiverCatList,
        'receiversubcatdict' : receiverSubCat,
        'mapload' : mapload,
        'mapanalytics' : mapanalytics,
        'totalincidents' : totalIncidents,
        'corporateattacks' : corporateAttacks,
        'corporateattackspercent' : corporateAttacksPercent,
        'totalincidentsvg' : totalIncidentSvg,
        'monthlyincidentsvg' : monthlyIncidentSvg,
        'map' : mapSvg,
        'continentlist' : continents.continentList,
    }
    if selected != None:
        context.update({
            'continent' : selectDict['selectcontinent'],
            'continenttotal' : totalContinent,
            'continenttotalpercent' : totalContinentPercent,
            'continentcorporate' : corpContinentAttacks,
            'continentcorporatepercent' : corpContinentAttacksPercent,
            'continentattacktypesvg' : continentAttackTypePieSvg,
            'continentattackerlocationsvg' : continentAttackerLocationPieSvg,
            'continentmitreaccesssvg' : continentMitreAccessPieSvg,
            'continenttotalintensity' : continentTotalIntensity,
            'continentmitreimpactsvg' : continentMitreImpactBarChart,
        })      
    return render(request, "index.html", context)

# about us page function
def about(request):
    githubRepoLink = "https://github.com/DanAlexCox/Cartobreach"
    context = {
        'index' : "..",
        'aboutus' : "",
        'sources' : "../sources/",
        'repolink': githubRepoLink,
    }
    return render(request,"about.html", context)

# sources page dictionary function
def source(request):
    # list of columns included in sources table
    columnList = ['incident_id', 'start_date', 'incident_type', 'receiver_country', 'source_url']
    
    # get request parameters submitted from index.html
    getStartDate = request.GET.get('sourcestartdate','2000-01-01')
    getEndDate = request.GET.get('sourceenddate','2025-01-01')
    getOrderSwitch = request.GET.get('orderswitch', None)
    # incidentType = request.GET.get # doesn't exist in filter yet
    getContinent = request.GET.get('continent')
    getCountry = request.GET.get('country')
    getCountrySearch = request.GET.get('countrysearch',"")
    
    # get dataset series
    df = dataset.pd.read_csv("Cartobreach/csv/eurepoc_global_dataset_1_3.csv", usecols=columnList)
    
    # change start and end date to datetime
    minDate = datetime.strptime(getStartDate, '%Y-%m-%d')
    maxDate = datetime.strptime(getEndDate, '%Y-%m-%d')
    
    # filter dataset by start and end date (same as index date filter)
    df = dataset.filterDateRange(df, df["start_date"], minDate.strftime('%d.%m.%Y'), maxDate.strftime('%d.%m.%Y'))
    
    # clean receiver countries NOT ALPHA 2 CODE
    df['receiver_country'] = dataset.cleanColumn(df['receiver_country'])
    
    # remove whitespace
    getCountrySearch = getCountrySearch.strip()
    
    # get list of countries to filter dataset
    countrySearchList = str.split(getCountrySearch, ";")
    while '' in countrySearchList:
        countrySearchList.remove('')
    
    # print(dataset.countUncleanColumnValues(df['receiver_country'], 'China'))
    # filter dataset that include all searching countries (i.e. SELECT countries OR other countries), ensuring no deplicates
    totalDf = None
    for oneSearch in countrySearchList:
        oneSearch = oneSearch.strip() # removes any white space on left or right
        singleDf = dataset.filterSpecificColumn(df, df['receiver_country'], oneSearch)
        totalDf = dataset.pd.concat([totalDf, singleDf])
    
    # convert totalDf list into tuple. drop_duplicates doesnt has lists
    for col in totalDf.columns:
        totalDf[col] = totalDf[col].apply(
            lambda x: tuple(x) if isinstance(x, list) else x
        )
    
    # remove duplicates
    df = totalDf.drop_duplicates()
    
    # count results after filtering/searching
    totalResults = len(df.index)
    
    # clean incident types
    df['incident_type'] = dataset.cleanColumn(df['incident_type'])
    
    # clean database column "source_url"
    df['source_url'] = dataset.cleanColumn(df["source_url"])
    
    # sort into ascending order descending depending on getOrderSwitch
    if getOrderSwitch == 'on': # descending order
        order = False
    else: # ascending order
        order = True
    df = dataset.orderByDate(df,'start_date', order)
    
    tableList = []
    # convert mini dataset into list
    for _, row in df.iterrows():
        row['start_date'] = datetime.strftime(row['start_date'], '%d %B %Y') # 'number day' 'month name' 'full year'
        tableList.append(
            [
                row['incident_id'],
                row['start_date'],
                row['incident_type'],
                row['receiver_country'],
                row['source_url']
            ]
        )    
    # TASK: connect to index page if get request parameters from index known (in current url), filter "source_url"

    context = {
        "index" : "..",
        "aboutus" :"../aboutus/",
        "sources" : "",
        "filterstartdate" : getStartDate,
        "filterenddate" : getEndDate,
        "order" : getOrderSwitch,
        "countrysearch" : getCountrySearch,
        "totalcount" : totalResults,
        "tablelist" : tableList,
    }
    return render(request, "sources.html", context)

# JSON function that deals with source.py autocomplete bar
def jsonsearch(request):
    query = request.GET.get('countrysearch',"").lower()
    
    # split by semicolons for multi-country search
    queryList = [c.strip() for c in query.split(";") if c.strip()]
    
    currentSearch = queryList[-1].lower() if queryList else ""
    
    results = []
    if currentSearch:
        for c in countryList:
            name = c.getName()
            if currentSearch in name.lower():
                results.append(name)
            if len(results) == 10:
                break
    return JsonResponse(results, safe=False)