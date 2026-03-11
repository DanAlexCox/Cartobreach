from django.shortcuts import render
from django.utils.safestring import mark_safe
from django import template
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import redirect
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
    # check if popup button was clicked, remove either continent or country from the url
    if request.method == "POST" and request.POST.get("popup") == "close":
        params = request.GET.copy()
        params.pop("continent", None)
        params.pop("country", None)
        query = continents.urlencode(params)
        url = request.path
        if query:
            url = f"{url}?{query}"
        return redirect(url)
    
    # template requests
        # get region switch info (default to continents if not known)
    selectRegion = request.GET.get('region', None) # on or None
    selectGroup = request.GET.get('group', None) # on or None
    startStartDate = request.GET.get('startdate', '2020-01-01')
    endStartDate = request.GET.get('enddate', '2025-01-01')
    selectedReceiverCat = request.GET.getlist("receivertype")
    selectedReceiverSubCat = request.GET.getlist("receiversubtype")
    mapanalytics = request.POST.get('mapanalytics')
    filterReset = request.POST.get('reset')
    popUpClose = request.POST.get('popup')
    mapload = None
    
    if filterReset == 'reset':
        print('Reset Successful')
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
    if popUpClose != 'close': # check if close button is pressed to hide code
        if selectRegion == None:
            getCountry = None
            getContinent = request.GET.get('continent') # load GET continent (value should be .getAlphaCode())
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
    if totalIncidents > 0:
        criticalAttacks = dataset.countUncleanColumnValues(ds["receiver_category"], categories.ci.getCatType()) # total critical infrastructure attacks in filtered dataset
        if totalIncidents > 0:
            criticalAttacksPercent = round((float(criticalAttacks) / float(totalIncidents)) * 100, 2) # critical infrastructure attacks percentage in filter dataset
        else:
            criticalAttacksPercent = 0
    
        if mapanalytics not in valid_includes:
            mapanalytics = None

        # convert country alpha codes for receivers and attackers
        ds["initiator_alpha_2"] = dataset.cleanColumn(ds["initiator_alpha_2"])
        ds["initiator_continent_code"] = ds["initiator_alpha_2"].apply(dataset.convertCountryCodeToContinentCode)
        ds["initiator_continent_code"] = ds["initiator_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
        
        ds["receiver_country_alpha_2_code"] = dataset.cleanColumn(ds["receiver_country_alpha_2_code"])
        ds["receiver_continent_code"] = ds["receiver_country_alpha_2_code"].apply(dataset.convertCountryCodeToContinentCode)
        ds["receiver_continent_code"] = ds["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
        
        # get current full url path for adding specific region onto it
        full_url = request.get_full_path()
        
        # order dataset in descending order by start_date for retrieving recent incident, see recentIncidentName and recentIncidentDate
        ds = dataset.orderByDate(ds,'start_date', False)
        
        # map section
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
                        
                        # get most recent name and start_date and add to continent objects
                        recentIncidentDate = countrySet['start_date'].max()
                        recentIncidentName = (countrySet.iloc[countrySet['start_date'].argmax()])['name']
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
                        
                        # get most recent name and start_date and add to continent objects
                        recentIncidentDate = continentSet['start_date'].max()
                        recentIncidentName = (continentSet.iloc[continentSet['start_date'].argmax()])['name']
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
                        recentIncidentDate = countrySet['start_date'].max()
                        recentIncidentName = (countrySet.iloc[countrySet['start_date'].argmax()])['name']
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
                        recentIncidentDate = continentSet['start_date'].max()
                        recentIncidentName = (continentSet.iloc[continentSet['start_date'].argmax()])['name']
                        
                        continentSingle.setRecentName(recentIncidentName)
                        continentSingle.setRecentDate(datetime.strftime(recentIncidentDate, '%d.%m.%Y'))
                        
                        
                # load continents map
                svg = continents.renderContinentMap(totalIncidents, full_url)
                
        mapSvg = mark_safe(svg)
        
        if mapanalytics != None:
            # Render graphs for attackers or receivers and continents or countries in global analysis
            totalIncidentSvg = mark_safe(dataset.yearlyIncidentBarPlot(ds, filterStartDate, filterEndDate))
            if selectRegion == 'on': # country
                # make list of country codes from premade countryList
                countryCodeList = []
                for code in countries.countryList:
                    countryCodeList.append(code.getAlphaCodeUp())
                if selectGroup == 'on': # attacker
                    quarterIncidentSvg = mark_safe(dataset.quarterAllAreasIncidentLinePlot(ds, ds["initiator_alpha_2"], countryCodeList, filterStartDate, filterEndDate))
                else: # receiver
                    quarterIncidentSvg = mark_safe(dataset.quarterAllAreasIncidentLinePlot(ds, ds["receiver_country_alpha_2_code"], countryCodeList, filterStartDate, filterEndDate))
            else: # continent
                # make list of continent codes from premade continentList
                continentCodeList = []
                for code in continents.continentList:
                    continentCodeList.append(code.getAlphaCode())
                if selectGroup == 'on': # attacker
                    quarterIncidentSvg = mark_safe(dataset.quarterAllAreasIncidentLinePlot(ds, ds["initiator_continent_code"], continentCodeList, filterStartDate, filterEndDate))
                else: # receiver
                    quarterIncidentSvg = mark_safe(dataset.quarterAllAreasIncidentLinePlot(ds, ds["receiver_continent_code"], continentCodeList, filterStartDate, filterEndDate))
        else:
            totalIncidentSvg = None
            quarterIncidentSvg = None
    
        # selected a map region
        selected = None
        if getContinent or getCountry:
            if selectRegion == None: # continent
                for i in continents.continentList: 
                    if i.getAlphaCode() == getContinent:
                        selected = i
                        selectDict['selectcontinent'] = selected.getName()
                        regionCode = selected.getAlphaCode()
                        if selectGroup == 'on': # attacker
                            regionCodeColumnName = 'initiator_continent_code'
                        else: # receiver
                            regionCodeColumnName = 'receiver_continent_code'
            elif selectRegion == 'on': # country
                for i in countryList: 
                    if i.getAlphaCodeUp() == getCountry:
                        selected = i
                        selectDict['selectcountry'] = selected.getName()
                        regionCode = selected.getAlphaCodeUp()
                        if selectGroup == 'on': # attacker
                            regionCodeColumnName = 'initiator_alpha_2'
                        else: # receiver
                            regionCodeColumnName = 'receiver_country_alpha_2_code'
            else:
                print("Not good")
            
            # filters dataset based on selected region
            regionSet = dataset.filterSpecificColumn(ds, ds[regionCodeColumnName], regionCode)
            # analytics of a region
            total = len(regionSet.index) # total incidents in region
            # check if region has existing incidents, otherwise make every variable = 0 or 'No known incidents affected this area'
            if total > 0:
                totalRegionPercent = round((float(total)/float(len(ds.index)) * 100), 2) # percentage of total incidents in region of filtered dataset
                # incident type analysis
                inciRegionSet = dataset.cleanColumn(regionSet["incident_type"]) # clean incident type column of region dataset
                regionAttackTypePieChart = dataset.pieChart(inciRegionSet, "Recorded Incident Types Within "+str(selected.getName())) # make pie chart of incident type in region
                regionAttackTypePieSvg = mark_safe(regionAttackTypePieChart)
                # critical infrastructure analysis
                regionCriticalSet = dataset.filterSpecificColumn(regionSet, regionSet['receiver_category'], categories.ci.getCatType()) # filter region by category
                regionCriticalCount = len(regionCriticalSet.index)
                regionCriticalPercent = round((float(regionCriticalCount)/float(total) * 100), 2)
                # critical infrastructure subcategory graph
                regionCriticalSet['receiver_subcategory'] = dataset.cleanColumn(regionCriticalSet['receiver_subcategory'])
                regionCriticalChart = dataset.barChartSpecific(regionCriticalSet['receiver_subcategory'], "Critical Infrastructure Categories", categories.ci.getCatSubType())
                regionCriticalSvg = mark_safe(regionCriticalChart)
                # mitre initial access
                regionMitreAccessSet = dataset.cleanColumn(regionSet["mitre_initial_access"]) # clean incident type column of region dataset
                regionMitreAccessPieChart = dataset.pieChart(regionMitreAccessSet, "Known Recorded Infiltration Types") # make pie chart of infiltration type in region
                regionMitreAccessPieSvg = mark_safe(regionMitreAccessPieChart)
                # mitre impact bar chart
                regionMitreImpactSet = dataset.cleanColumn(regionSet["mitre_impact"]) # clean mitre impacts for region dataset
                regionMitreImpactBarChart = dataset.barChart(regionMitreImpactSet, "Known Recorded Mitre Impact Methods") # make bar chart of mitre impact methods in region
                regionMitreImpactBarChart = mark_safe(regionMitreImpactBarChart)
                # number of attacks on social groups
                regionSocialSet = dataset.filterSpecificColumn(regionSet, regionSet['receiver_category'], categories.sg.getCatType()) # filter region by category
                regionSocialCount = len(regionSocialSet.index)
                regionSocialPercent = round((float(regionSocialCount)/float(total) * 100), 2)
                # social groups subcategory graph
                regionSocialSet['receiver_subcategory'] = dataset.cleanColumn(regionSocialSet['receiver_subcategory'])
                regionSocialChart = dataset.barChartSpecific(regionSocialSet['receiver_subcategory'], "Social Group Categories", categories.sg.getCatSubType())
                regionSocialSvg = mark_safe(regionSocialChart)
                # number of attacks on political groups
                regionPoliticSet = dataset.filterSpecificColumn(regionSet, regionSet['receiver_category'], categories.sips.getCatType()) # filter region by category
                regionPoliticCount = len(regionPoliticSet.index)
                regionPoliticPercent = round((float(regionPoliticCount)/float(total) * 100), 2)
                # political groups subcategory graph
                regionPoliticSet['receiver_subcategory'] = dataset.cleanColumn(regionPoliticSet['receiver_subcategory'])
                regionPoliticChart = dataset.barChartSpecific(regionPoliticSet['receiver_subcategory'], "State Institutions & Political System Categories", categories.sips.getCatSubType())
                regionPoliticSvg = mark_safe(regionPoliticChart)
                # number of attacks on multiple continents
                regionMultiSet = dataset.filterMultipleColumns(regionSet, regionSet[regionCodeColumnName]) # filter region by multiple region targets
                regionMultiCount = len(regionMultiSet.index)
                regionMultiPercent = round((float(regionMultiCount)/float(total) * 100), 2)
                # get attribution sources list
                regionSet['source_url'] = dataset.cleanColumn(regionSet['source_url'])
                attributeList = []
                for sourceList in regionSet['source_url']: 
                    attributeList = attributeList+sourceList
                # get source domain and unique domain list
                domainList = []
                uniqueList = []
                for source in attributeList:
                    source = source.split('/')
                    if "https:" in source[0]:
                        domainList.append(source[2])
                        if source[2] not in uniqueList:
                            uniqueList.append(source[2])
                
                # get domain popularity count and organise urls into domain locations
                countList = []
                listDomainList = []
                for uniqueDomain in uniqueList:
                    # count occurrences in domainList
                    countDomain = domainList.count(uniqueDomain)
                    countList.append(countDomain)
                    # collect attributes that contain the domain
                    uniqueDomainList = [attribute for attribute in attributeList if uniqueDomain in attribute]
                    # limit to max 5
                    uniqueDomainList = uniqueDomainList[:5]
                    listDomainList.append(uniqueDomainList)
                
                # new panda dataframe
                upd = dataset.pd.DataFrame(
                    {
                        "domain_url" : uniqueList,
                        "source_url" : listDomainList,
                        "domain_count" : countList
                    }
                )
                # convert highest 5 domain counts from dataframe into list
                updTopFive = upd.nlargest(5, ['domain_count'])
                domainTopList = []
                for i in range(len(updTopFive.index)):
                    rowList = [] # constructing row data into list
                    rowList.append([updTopFive.iloc[i]['domain_url']]) # make list despite being single, for iteration if
                    rowList.append([updTopFive.iloc[i]['domain_count']]) # make list despite being single, for iteration if
                    rowList.append(updTopFive.iloc[i]['source_url'])
                    domainTopList.append(rowList)
                
                # remove selected country from countrylist
                removedCodeList = []
                for nonSelect in continents.continentList:
                    if nonSelect != selected: # avoid removing selected from list, will impact the dataset after usage
                        removedCodeList.append(nonSelect.getAlphaCode())
                # multiple target, specify other countries
                regionMultiChart = dataset.barChartSpecific(regionSet[regionCodeColumnName], "Other Continents That Were Also Targeted", removedCodeList)
                regionMultiSvg = mark_safe(regionMultiChart)
        else:
            print('invalid input')
    else:
        criticalAttacks = 0
        criticalAttacksPercent = 0
        totalIncidentSvg = "No data within filtered range"
        quarterIncidentSvg = "No data within filtered range"
        mapSvg = "No data within filtered range"
        selected = None
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
        'quartersvg' : quarterIncidentSvg,
        'map' : mapSvg,
    }
    if selected != None:
        if getReceiver != None:
            context.update({ 'receiver' : getReceiver, }) # signal to template to include receiver data
            if getContinent != None:
                context.update({
                    'continent' : selectDict['selectcontinent'],
                })
            elif getCountry != None:
                context.update({
                    'country' : selectDict['selectcountry'],
                })
        elif getAttacker != None:
            context.update({ 'attacker' : getAttacker, }) # signal to template to include attacker data
            if getContinent != None:
                context.update({
                    'continent' : selectDict['selectcontinent'],
                })
            elif getCountry != None:
                context.update({
                    'country' : selectDict['selectcountry'],
                })
        context.update({
            'total' : total, # region analysis
            'totalpercent' : totalRegionPercent,
            'attacktypesvg' : regionAttackTypePieSvg, # incident type analysis
            'mitreaccesssvg' : regionMitreAccessPieSvg, # mitre analysis
            'mitreimpactsvg' : regionMitreImpactBarChart,
            'criticaltotal' : regionCriticalPercent, # critical infrastructure analysis
            'criticalpercent' : regionCriticalCount,
            'criticalsvg': regionCriticalSvg,
            'socialtotal' : regionSocialCount, # social group analysis
            'socialpercent' : regionSocialPercent,
            'socialsvg' : regionSocialSvg,
            'politictotal' : regionPoliticCount, # political group analysis
            'politicpercent' : regionPoliticPercent,
            'politicsvg' : regionPoliticSvg,
            'multitotal' : regionMultiCount, # multi target analysis
            'multipercent' : regionMultiPercent,
            'multisvg' : regionMultiSvg,
            'sourcetable' : domainTopList # nested list
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
    
    if getCountrySearch:
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