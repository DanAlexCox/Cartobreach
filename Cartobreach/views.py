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
    selectGroup = request.GET.get('group', None) # on or None
    startStartDate = request.GET.get('startdate', '2020-01-01')
    endStartDate = request.GET.get('enddate', '2025-01-01')
    selectedReceiverCat = request.GET.getlist("receivertype")
    selectedReceiverSubCat = request.GET.getlist("receiversubtype")
    mapanalytics = request.POST.get('mapanalytics')
    mapload = None
    
    # make select dictionary
    selectDict = {}
    selectDict['switchregion'] = selectRegion
    selectDict['switchgroup'] = selectGroup
    selectDict['filterstartdate'] = startStartDate
    selectDict['filterenddate'] = endStartDate
    selectDict['filterreceivercategorylist'] = selectedReceiverCat
    selectDict['filterreceiversubcategorylist'] = selectedReceiverSubCat
    
    # condition requests
    # find out if continent or country is selected on map
    if selectRegion == None:
        getContinent = request.GET.get('continent') # load GET continent (value should be .getAlphaCode())
        getCountry = None
        selectDict['receivercontinent'] = getContinent # dictionary add
    elif selectRegion == 'on':
        getContinent = None
        getCountry = request.GET.get('country') # load GET country (value should be .getAlphaCodeUp())
        selectDict['receivercountry'] = getCountry # dictionary add
    else:
        getContinent = request.GET.get('continent') # load GET continent (value should be .getAlphaCode())
        getCountry = None
        selectRegion = None
    
    # find out if receiver or attacker is selected from switches
    if selectGroup == 'on':
        getReceiver = None
        getAttacker = 'on' 
    else:
        getReceiver = 'on'
        getAttacker = None 
    
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
    totalIncidents = len(ds.index) # total incidents in filtered dataset
    
    criticalAttacks = dataset.countUncleanColumnValues(ds["receiver_category"], categories.ci.getCatType()) # total critical infrastructure attacks in filtered dataset
    criticalAttacksPercent = round((float(criticalAttacks) / float(totalIncidents)) * 100, 2) # critical infrastructure attacks percentage in filter dataset
   
    if mapanalytics not in valid_includes:
        mapanalytics = None

    # convert country alpha codes for receivers and attackers    
    if selectGroup == 'on': # i.e. attacker selected
        ds["initiator_alpha_2"] = dataset.cleanColumn(ds["initiator_alpha_2"])
        ds["initiator_continent_code"] = ds["initiator_alpha_2"].apply(dataset.convertCountryCodeToContinentCode)
        ds["initiator_continent_code"] = ds["initiator_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    else: # i.e. receiver selected/defaulted to
        ds["receiver_country_alpha_2_code"] = dataset.cleanColumn(ds["receiver_country_alpha_2_code"])
        ds["receiver_continent_code"] = ds["receiver_country_alpha_2_code"].apply(dataset.convertCountryCodeToContinentCode)
        ds["receiver_continent_code"] = ds["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    
    # get current full url path for adding specific region onto it
    full_url = request.get_full_path()
    
    # order dataset in descending order by start_date for retrieving recent incident, see recentIncidentName and recentIncidentDate
    ds = dataset.orderByDate(ds,'start_date', False)
    
    # check what group is selected, change between attacker (on) and receiver (Default: None)
    # check what region is selected, change between continents (default: None) and countries (on)
    if selectGroup == 'on': # attacker
        if selectRegion == 'on': 
            # set total incident values for each country
            for countrySingle in countries.countryList:
                countrySet = dataset.filterSpecificColumn(ds, ds["initiator_alpha_2"], countrySingle.getAlphaCodeUp())
                countrySingle.setValue(len(countrySet.index))
                # set country information for tooltip
                if len(countrySet.index) > 0:
                    countrySet['incident_type'] = dataset.cleanColumn(countrySet['incident_type'])
                    mostInci = countrySet['incident_type'].explode().value_counts()
                    mostInciType = mostInci.index[0]    # value of most popular incident type
                    mostInciCount = mostInci.iloc[0]    # count of most popular incident type
                    countrySingle.setMostInci(mostInciType)
                    countrySingle.setMostInciCount(int(mostInciCount))
                    
                    # criticalInfraCount = dataset.countUncleanColumnValues(countrySet['receiver_category'], 'Critical infrastructure') # counting critical infrastructure incidents
                    # countrySingle.setCritInfraCount(int(criticalInfraCount))
                    
                    # eduCount = dataset.countUncleanColumnValues(countrySet['receiver_category'], 'Education') # counting education incidents
                    # countrySingle.setEduCount(int(eduCount))
                    
                    # multiCountryFiltered = dataset.filterMultipleColumns(countrySet, countrySet['initiator_alpha_2'])
                    # countrySingle.setMultiCount(len(multiCountryFiltered.index))
                    
                    # get most recent name and start_date and add to continent objects
                    recentIncidentName = countrySet['name'].explode().value_counts().index[0]
                    recentIncidentDate = countrySet['start_date'].explode().value_counts().index[0]
                    countrySingle.setRecentName(recentIncidentName)
                    countrySingle.setRecentDate(datetime.strftime(recentIncidentDate, '%d.%m.%Y'))
                    
            # load countrys map
            svg = countries.renderCountryMap(totalIncidents, full_url)
        else: # i.e. continent selected/defaulted to
            # set total incident values for continents
            for continentSingle in continents.continentList:
                continentSet = dataset.filterSpecificColumn(ds, ds["initiator_continent_code"], continentSingle.getAlphaCode()) # filter date filted range for each continent
                continentSingle.setValue(len(continentSet.index)) # total incidents in continent
                
                # set contient information for tooltip
                if len(continentSet.index) > 0:
                    continentSet['incident_type'] = dataset.cleanColumn(continentSet['incident_type'])
                    mostInci = continentSet['incident_type'].explode().value_counts()
                    mostInciType = mostInci.index[0]    # value of most popular incident type
                    mostInciCount = mostInci.iloc[0]    # count of most popular incident type
                    continentSingle.setMostInci(mostInciType)
                    continentSingle.setMostInciCount(int(mostInciCount))
                    
                    # criticalInfraCount = dataset.countUncleanColumnValues(continentSet['receiver_category'], 'Critical infrastructure') # counting critical infrastructure incidents
                    # continentSingle.setCritInfraCount(int(criticalInfraCount))
                    
                    # eduCount = dataset.countUncleanColumnValues(continentSet['receiver_category'], 'Education') # counting education incidents
                    # continentSingle.setEduCount(int(eduCount))
                    
                    # multiCountryFiltered = dataset.filterMultipleColumns(continentSet, continentSet['receiver_continent_code'])
                    # continentSingle.setMultiCount(len(multiCountryFiltered.index))
                    
                    # get most recent name and start_date and add to continent objects
                    recentIncidentName = continentSet['name'].explode().value_counts().index[0]
                    recentIncidentDate = continentSet['start_date'].explode().value_counts().index[0]
                    continentSingle.setRecentName(recentIncidentName)
                    continentSingle.setRecentDate(datetime.strftime(recentIncidentDate, '%d.%m.%Y'))
                    
            # load continents map
            svg = continents.renderContinentMap(totalIncidents, full_url)
    else: # receiver
        if selectRegion == 'on': 
            # set total incident values for each country
            for countrySingle in countries.countryList:
                countrySet = dataset.filterSpecificColumn(ds, ds["receiver_country_alpha_2_code"], countrySingle.getAlphaCodeUp())
                countrySingle.setValue(len(countrySet.index))
                # set country information for tooltip
                if len(countrySet.index) > 0:
                    countrySet['incident_type'] = dataset.cleanColumn(countrySet['incident_type'])
                    mostInci = countrySet['incident_type'].explode().value_counts()
                    mostInciType = mostInci.index[0]    # value of most popular incident type
                    mostInciCount = mostInci.iloc[0]    # count of most popular incident type
                    countrySingle.setMostInci(mostInciType)
                    countrySingle.setMostInciCount(int(mostInciCount))
                    
                    criticalInfraCount = dataset.countUncleanColumnValues(countrySet['receiver_category'], 'Critical infrastructure') # counting critical infrastructure incidents
                    countrySingle.setCritInfraCount(int(criticalInfraCount))
                    
                    eduCount = dataset.countUncleanColumnValues(countrySet['receiver_category'], 'Education') # counting education incidents
                    countrySingle.setEduCount(int(eduCount))
                    
                    multiCountryFiltered = dataset.filterMultipleColumns(countrySet, countrySet['initiator_alpha_2'])
                    countrySingle.setMultiCount(len(multiCountryFiltered.index))
                    
                    # get most recent name and start_date and add to continent objects
                    recentIncidentName = countrySet['name'].explode().value_counts().index[0]
                    recentIncidentDate = countrySet['start_date'].explode().value_counts().index[0]
                    countrySingle.setRecentName(recentIncidentName)
                    countrySingle.setRecentDate(datetime.strftime(recentIncidentDate, '%d.%m.%Y'))
                    
            # load countrys map
            svg = countries.renderCountryMap(totalIncidents, full_url)
        else: # i.e. continent selected/defaulted to
            # set total incident values for continents
            for continentSingle in continents.continentList:
                continentSet = dataset.filterSpecificColumn(ds, ds["receiver_continent_code"], continentSingle.getAlphaCode()) # filter date filted range for each continent
                continentSingle.setValue(len(continentSet.index)) # total incidents in continent
                
                # set contient information for tooltip
                if len(continentSet.index) > 0:
                    continentSet['incident_type'] = dataset.cleanColumn(continentSet['incident_type'])
                    mostInci = continentSet['incident_type'].explode().value_counts()
                    mostInciType = mostInci.index[0]    # value of most popular incident type
                    mostInciCount = mostInci.iloc[0]    # count of most popular incident type
                    continentSingle.setMostInci(mostInciType)
                    continentSingle.setMostInciCount(int(mostInciCount))
                    
                    criticalInfraCount = dataset.countUncleanColumnValues(continentSet['receiver_category'], 'Critical infrastructure') # counting critical infrastructure incidents
                    continentSingle.setCritInfraCount(int(criticalInfraCount))
                    
                    eduCount = dataset.countUncleanColumnValues(continentSet['receiver_category'], 'Education') # counting education incidents
                    continentSingle.setEduCount(int(eduCount))
                    
                    multiCountryFiltered = dataset.filterMultipleColumns(continentSet, continentSet['receiver_continent_code'])
                    continentSingle.setMultiCount(len(multiCountryFiltered.index))
                    
                    # get most recent name and start_date and add to continent objects
                    recentIncidentName = continentSet['name'].explode().value_counts().index[0]
                    recentIncidentDate = continentSet['start_date'].explode().value_counts().index[0]
                    continentSingle.setRecentName(recentIncidentName)
                    continentSingle.setRecentDate(datetime.strftime(recentIncidentDate, '%d.%m.%Y'))
                    
            # load continents map
            svg = continents.renderContinentMap(totalIncidents, full_url)
            
    mapSvg = mark_safe(svg)
    # Render graphs for attackers or receivers
    if selectGroup == 'on':
        totalIncidentSvg = mark_safe(dataset.yearlyIncidentBarPlot(ds, filterStartDate, filterEndDate))
        monthlyIncidentSvg = mark_safe(dataset.monthlyAllAreasIncidentLinePlot(ds, ds["initiator_continent_code"], filterStartDate, filterEndDate))
    else:
        totalIncidentSvg = mark_safe(dataset.yearlyIncidentBarPlot(ds, filterStartDate, filterEndDate))
        monthlyIncidentSvg = mark_safe(dataset.monthlyAllAreasIncidentLinePlot(ds, ds["receiver_continent_code"], filterStartDate, filterEndDate))

    selected = None
    if selectRegion == None:
        for i in continents.continentList: 
            if i.getAlphaCode() == getContinent:
                selected = i
                selectDict['selectcontinent'] = selected.getName()
                # filters dataset based on selected continent
                contSet = dataset.filterSpecificColumn(ds, ds["receiver_continent_code"], selected.getAlphaCode())
                # analytics of a continent
                totalContinent = len(contSet.index) # total continent incidents
                totalContinentPercent = round((float(totalContinent)/float(len(ds.index)) * 100), 2) # percentage of total incidents in continent of filtered dataset
                # incident type analysis
                inciContSet = dataset.cleanColumn(contSet["incident_type"]) # clean incident type column of continent dataset
                continentAttackTypePieChart = dataset.pieChart(inciContSet, "Recorded Incident Types Within Continent") # make pie chart of incident type in continent
                continentAttackTypePieSvg = mark_safe(continentAttackTypePieChart)
                # critical infrastructure analysis
                continentCriticalSet = dataset.filterSpecificColumn(contSet, contSet['receiver_category'], categories.ci.getCatType()) # filter continent by category
                continentCriticalCount = len(continentCriticalSet.index)
                continentCriticalPercent = round((float(continentCriticalCount)/float(totalContinent) * 100), 2)
                # critical infrastructure subcategory graph
                continentCriticalSet['receiver_subcategory'] = dataset.cleanColumn(continentCriticalSet['receiver_subcategory'])
                continentCriticalChart = dataset.barChartSpecific(continentCriticalSet['receiver_subcategory'], "Critical Infrastructure Categories", categories.ci.getCatSubType())
                continentCriticalSvg = mark_safe(continentCriticalChart)
                # make attacker continent code and pie chart
                contSet["initiator_alpha_2"] = dataset.cleanColumn(contSet["initiator_alpha_2"])
                contSet["initiator_continent_code"] = contSet["initiator_alpha_2"].apply(dataset.convertCountryCodeToContinentCode)
                contSet["initiator_continent_code"] = contSet["initiator_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
                continentAttackerLocationPieChart = dataset.pieChart(contSet["initiator_continent_code"], "Known Attacker Locations")
                continentAttackerLocationPieSvg = mark_safe(continentAttackerLocationPieChart)
                # mitre initial access
                mitreAccessContSet = dataset.cleanColumn(contSet["mitre_initial_access"]) # clean incident type column of continent dataset
                continentMitreAccessPieChart = dataset.pieChart(mitreAccessContSet, "Known Recorded Infiltration Types") # make pie chart of infiltration type in continent
                continentMitreAccessPieSvg = mark_safe(continentMitreAccessPieChart)
                # total weighted intensity of continent
                contSet["weighted_intensity"] = dataset.pd.to_numeric(contSet["weighted_intensity"], errors="coerce") # no need to call dataset.totalAreaIntensity, contSet is filtered and cleaned
                continentTotalIntensity = contSet["weighted_intensity"].sum()
                # mitre impact bar chart
                mitreImpactContSet = dataset.cleanColumn(contSet["mitre_impact"]) # clean mitre impacts for continent dataset
                continentMitreImpactBarChart = dataset.barChart(mitreImpactContSet, "Known Recorded Mitre Impact Methods") # make bar chart of mitre impact methods in continent
                continentMitreImpactBarChart = mark_safe(continentMitreImpactBarChart)
                break
    elif selectRegion == 'on':
        for i in countryList: 
            if i.getAlphaCodeUp() == getCountry:
                selected = i
                selectDict['selectcountry'] = selected.getName()
                # filter dataset
                countSet = dataset.filterSpecificColumn(ds, ds["receiver_country_alpha_2_code"], selected.getAlphaCodeUp())
                # total recorded incidents
                totalCountry = len(countSet.index)
                totalCountryPercent = round((float(totalCountry)/float(len(ds.index)) * 100), 2)
                # incident types graph
                countryInciCountSet = dataset.cleanColumn(countSet["incident_type"]) # clean incident type column of continent dataset
                countryIncidentTypePieChart = dataset.pieChart(countryInciCountSet, "Incident Types Within Country") # TASK: FIX PYGAL TITLE IN DATASET.PY
                countryIncidentTypePieSvg = mark_safe(countryIncidentTypePieChart)
                # number of attacks on critical infrastructure
                countryCriticalSet = dataset.filterSpecificColumn(countSet, countSet['receiver_category'], categories.ci.getCatType()) # filter country by category
                countryCriticalCount = len(countryCriticalSet.index)
                countryCriticalPercent = round((float(countryCriticalCount)/float(totalCountry) * 100), 2)
                # critical infrastructure subcategory graph
                countryCriticalSet['receiver_subcategory'] = dataset.cleanColumn(countryCriticalSet['receiver_subcategory'])
                countryCriticalChart = dataset.barChartSpecific(countryCriticalSet['receiver_subcategory'], "Critical Infrastructure Categories", categories.ci.getCatSubType())
                countryCriticalSvg = mark_safe(countryCriticalChart)
                # number of attacks on social groups
                countrySocialSet = dataset.filterSpecificColumn(countSet, countSet['receiver_category'], categories.sg.getCatType()) # filter country by category
                countrySocialCount = len(countrySocialSet.index)
                countrySocialPercent = round((float(countryCriticalCount)/float(totalCountry) * 100), 2)
                # social groups subcategory graph
                countrySocialSet['receiver_subcategory'] = dataset.cleanColumn(countrySocialSet['receiver_subcategory'])
                countrySocialChart = dataset.barChartSpecific(countrySocialSet['receiver_subcategory'], "Social Group Categories", categories.sg.getCatSubType())
                countrySocialSvg = mark_safe(countrySocialChart)
                # number of attacks on political groups
                countryPoliticSet = dataset.filterSpecificColumn(countSet, countSet['receiver_category'], categories.sips.getCatType()) # filter country by category
                countryPoliticCount = len(countryPoliticSet.index)
                countryPoliticPercent = round((float(countryPoliticCount)/float(totalCountry) * 100), 2)
                # political groups subcategory graph
                countryPoliticSet['receiver_subcategory'] = dataset.cleanColumn(countryPoliticSet['receiver_subcategory'])
                countryPoliticChart = dataset.barChartSpecific(countryPoliticSet['receiver_subcategory'], "State Institutions & Political System Categories", categories.sips.getCatSubType())
                countryPoliticSvg = mark_safe(countryPoliticChart)
                # number of attacks on multiple continents
                countryMultiSet = dataset.filterMultipleColumns(countSet, countSet['receiver_country_alpha_2_code']) # filter country by multiiple continent targets
                countryMultiCount = len(countryMultiSet.index)
                countryMultiPercent = round((float(countryMultiCount)/float(totalCountry) * 100), 2)
                # remove selected country from countrylist
                countryList.remove(selected)
                
                removedCodeList = []
                for nonSelect in countryList:
                    removedCodeList.append(nonSelect.getAlphaCodeUp())
                # multiple target, specify other countries
                countryMultiChart = dataset.barChartSpecific(countryMultiSet['receiver_country_alpha_2_code'], "Other Continents That Were Also Targeted", removedCodeList)
                countryMultiSvg = mark_safe(countryMultiChart)
                
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
        'switchgroup' : selectDict['switchgroup'],
        'receivercatlist' : receiverCatList,
        'receiversubcatdict' : receiverSubCat,
        'mapload' : mapload,
        'mapanalytics' : mapanalytics,
        'totalincidents' : totalIncidents,
        'criticalattacks' : criticalAttacks,
        'criticalattackspercent' : criticalAttacksPercent,
        'totalincidentsvg' : totalIncidentSvg,
        'monthlyincidentsvg' : monthlyIncidentSvg,
        'map' : mapSvg,
    }
    if selected != None:
        if getReceiver != None:
            context.update({ 'receiver' : getReceiver, }) # signal to template to include receiver data
            if getContinent != None:
                context.update({
                    'continent' : selectDict['selectcontinent'],
                    'continenttotal' : totalContinent, # overall continent analysis
                    'continenttotalpercent' : totalContinentPercent,
                    'continentcriticaltotal' : continentCriticalPercent, # critical infrastructure analysis
                    'continentcriticalpercent' : continentCriticalCount,
                    'continentcriticalsvg': continentCriticalSvg,
                    'continentattacktypesvg' : continentAttackTypePieSvg, # incident type analysis
                    'continentattackerlocationsvg' : continentAttackerLocationPieSvg,
                    'continenttotalintensity' : continentTotalIntensity, # intensity analysis
                    'continentmitreaccesssvg' : continentMitreAccessPieSvg, # mitre analysis
                    'continentmitreimpactsvg' : continentMitreImpactBarChart,
                })
            elif getCountry != None:
                context.update({
                    'country' : selectDict['selectcountry'],
                    'countrytotal' : totalCountry, # overall country analysis
                    'countrytotalpercent' : totalCountryPercent,
                    'countryincidenttypesvg' : countryIncidentTypePieSvg, # incident type analysis
                    'countrycriticaltotal' : countryCriticalCount, # critical infrastructure analysis
                    'countrycriticalpercent' : countryCriticalPercent,
                    'countrycriticalsvg' : countryCriticalSvg,
                    'countrysocialtotal' : countrySocialCount, # social group analysis
                    'countrysocialpercent' : countrySocialPercent,
                    'countrysocialsvg' : countrySocialSvg,
                    'countrypolitictotal' : countryPoliticCount, # political group analysis
                    'countrypoliticpercent' : countryPoliticPercent,
                    'countrypoliticsvg' : countryPoliticSvg,
                    'countrymultitotal' : countryMultiCount, # multi target analysis
                    'countrymultipercent' : countryMultiPercent,
                    'countrymultisvg' : countryMultiSvg,
                })
        elif getAttacker != None:
            context.update({ 'attacker' : getAttacker, }) # signal to template to include attacker data
            if getContinent != None:
                context.update({
                    'continent' : selectDict['selectcontinent'],
                    'continenttotal' : totalContinent, # overall continent analysis
                    'continenttotalpercent' : totalContinentPercent,
                    'continentcriticaltotal' : continentCriticalPercent, # critical infrastructure analysis
                    'continentcriticalpercent' : continentCriticalCount,
                    'continentcriticalsvg': continentCriticalSvg,
                    'continentattacktypesvg' : continentAttackTypePieSvg, # incident type analysis
                    'continentattackerlocationsvg' : continentAttackerLocationPieSvg,
                    'continenttotalintensity' : continentTotalIntensity, # intensity analysis
                    'continentmitreaccesssvg' : continentMitreAccessPieSvg, # mitre analysis
                    'continentmitreimpactsvg' : continentMitreImpactBarChart,
                })
            elif getCountry != None:
                context.update({
                    'country' : selectDict['selectcountry'],
                    'countrytotal' : totalCountry, # overall country analysis
                    'countrytotalpercent' : totalCountryPercent,
                    'countryincidenttypesvg' : countryIncidentTypePieSvg, # incident type analysis
                    'countrycriticaltotal' : countryCriticalCount, # critical infrastructure analysis
                    'countrycriticalpercent' : countryCriticalPercent,
                    'countrycriticalsvg' : countryCriticalSvg,
                    'countrysocialtotal' : countrySocialCount, # social group analysis
                    'countrysocialpercent' : countrySocialPercent,
                    'countrysocialsvg' : countrySocialSvg,
                    'countrypolitictotal' : countryPoliticCount, # political group analysis
                    'countrypoliticpercent' : countryPoliticPercent,
                    'countrypoliticsvg' : countryPoliticSvg,
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