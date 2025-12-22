# pip install ...
import matplotlib.pyplot as ppl # import pyplot matlablib
import pandas as pd # import pandas
import pycountry_convert as pcc # import pycountry-convert
import pygal as py
from datetime import datetime # import datetime function
from .continents import AF,AN,AS,EU,NA,OC,SA # import continent objects

pd.options.mode.chained_assignment = None

# get data from csv
df = pd.read_csv("Cartobreach/csv/eurepoc_global_dataset_1_3.csv")

# function that converts date formatted in DD.MM.YYYY
def convertDateTime(column):
    return pd.to_datetime(column, format="%d.%m.%Y", errors ='coerce')

# function that cleans and returns column series
def cleanColumn(column):
    # turn into uncleaned column lists
    countList = column.apply(lambda v: v.split(";") if isinstance(v, str) else (v if isinstance(v, list) else ([] if pd.isna(v) else [v])))
    # clean column lists to make unique values only
    return countList.apply(lambda x: list(dict.fromkeys(x)))

# function for counting how many instances are in an uncleaned column
def countUncleanColumnValues(column, search):
    # clean column and turn into list
    cleanedColumn = cleanColumn(column)
    return cleanedColumn.apply(lambda x: isinstance(x, list) and search in x).sum()

# function that converts country alpha codes to continents
def convertCountryCodeToContinentCode(cellList):
    continents = []
    for code in cellList:
        try:
            contCode = pcc.country_alpha2_to_continent_code(code)
            continents.append(contCode)
        except:
            continents.append("N/A")
    return continents

# function that counts how many times a data "search" is in an unclean column thats also have another data "alsosearch" from column "alsocolumn"
def countUncleanDoubleColumnValues(column, search, alsocolumn, alsosearch):
    # clean columns then count the rows that both search and also search exist
    
    return (cleanColumn(column).apply(lambda x: search in x) & cleanColumn(alsocolumn).apply(lambda x: alsosearch in x)).sum()

# function that filters out date type columns to exclude any non date times
def filterDateTime(series):
    # convert to DateTime
    series = series.apply(convertDateTime)
    return series[series.apply(lambda x: isinstance(x, datetime))]

# function that filters every row that doesnt have only value in each row
def filterSingleColumn(dataset, cellList):
    # clean column
    cellList = cleanColumn(cellList)
    return dataset[cellList.apply(lambda x: isinstance(x, list) and len(x) == 1)]

# function that filters every row that doesnt have only value in each row
def filterMultipleColumns(dataset, column):
    # clean column
    column = cleanColumn(column)
    return dataset[column.apply(lambda x: isinstance(x, list) and len(x) > 1)]

# function that filters a specific value from series
def filterSpecificColumn(dataset, column, value):
    # clean column
    cleanedColumn = cleanColumn(column)
    return dataset[cleanedColumn.apply(lambda x: value in x)]

# function that filters two different AND values from series
def filterTwoColumns(dataset, column, value, alsocolumn, alsovalue):
    # clean column and alsocolumn
    cleanedColumn = cleanColumn(column)
    cleanedAlsoColumn = cleanColumn(alsocolumn)
    # return df that is filtered when value and alsovalue exist
    return dataset[cleanedColumn.apply(lambda x: value in x) & cleanedAlsoColumn.apply(lambda x: alsovalue in x)]

# function that calculates total intensity of a region (continent/country) using weighted_intensity
def totalAreaIntensity(dataset, area, alpha):
    # filter to a region area
    filteredDataframe = filterSpecificColumn(dataset, area, alpha)
    # sum up weighted_intensity
    return filteredDataframe["weighted_intensity"].sum()
    
# function that calculates total intensity using 2 conditions
def totalMultipleIntensity(column, value, alsocolumn, alsovalue):
    # filter df and then sum up weighted_intensity
    return filterTwoColumns(column, value, alsocolumn, alsovalue)["weighted_intensity"].sum()

# function that calculates unweighted intensity of a region using a specified scoring column
def specificIntensity(scorecolumn, regioncolumn, region):
    # filter to region and replace score strings to integer scores then sum all points up
    return filterSpecificColumn(regioncolumn, region)[scorecolumn].apply(lambda x: 2 if "2 points" in x else (1 if "1 point" in x else 0)).sum()

# function that cuts data series into cut dates between minimum date and maximum
def filterDateRange(dataset, dateColumnSeries, min, max):
    filteredSeries = filterDateTime(dateColumnSeries) # filter date series
    if isinstance(min, str) and isinstance(max, str): # if min and max dates are string
        min = pd.Timestamp(datetime.strptime(min, '%d.%m.%Y')) #convert date string to datetime
        max = pd.Timestamp(datetime.strptime(max, '%d.%m.%Y')) #convert date string to datetime
    # union comparison of min and max ranges
    return dataset[filteredSeries.apply(lambda x: x >= min) & filteredSeries.apply(lambda x: x < max)]

# function that adds rows in a date range
def countInDateRange(dataset, dateColumnSeries, min, max):
    return filterDateRange(dataset, dateColumnSeries, min, max).count()

# function that constructs line plot for yearly incident counts between dataset minimum and maximum date
def yearlyIncidentLinePlot(dataset, dateColumnSeries, dataMin, dataMax):
    # yearly date range list
    yearRange = pd.date_range(start=dataMin, end=dataMax, freq='YS').to_pydatetime()
    # date range counts of each year (count up to end of year, end of year)
    x_values = []
    xtick_replace = []
    xtick_values = []
    y_values = []
    for i in range(0, len(yearRange)-1):
        x_values.append(str(yearRange[i]))
        if yearRange[i].year % 2 == 0: # determine x axis scale i.e. xticks
            xtick_replace.append(str(yearRange[i]))
            xtick_values.append(str(yearRange[i].year))
        y_values.append(countInDateRange(dataset, dateColumnSeries, yearRange[i], yearRange[i+1]))
    # plot line plot (x: year, y: number of incidents)
    ppl.figure()
    ppl.plot(x_values, y_values)
    ppl.xlabel("Year")
    ppl.xticks(xtick_replace, xtick_values)
    ppl.ylabel("No. of Incidents")
    ppl.savefig("Cartobreach/static/images/incidents_per_year.png")

# function that cuts data into specified range with one condition
def filterDataRange(dateColumnSeries, dataColumn, value, min, max):
    filteredSeries = filterDateTime(dateColumnSeries) # filter date series
    if isinstance(min, str) and isinstance(max, str): # if min and max dates are string
        min = pd.Timestamp(datetime.strptime(min, '%d.%m.%Y')) #convert date string to datetime
        max = pd.Timestamp(datetime.strptime(max, '%d.%m.%Y')) #convert date string to datetime
    # union of filtered dates and data column value
    return dataColumn[dataColumn.apply(lambda x: value in x) & filteredSeries.apply(lambda x: x >= min) & filteredSeries.apply(lambda x: x < max)]

# function that adds rows in data range
def countInDataRange(dateColumnSeries, dataColumn, value, min, max):
    return filterDataRange(dateColumnSeries, dataColumn, value, min, max).count()

# function that constructs a scatter plot with monthly incidents for all cleaned areas (continents/countries)(cleanColumn(...))
def monthlyAllAreasIncidentLinePlot(dateColumnSeries, cleanedArea):
    uniqueArea = cleanedArea.explode().unique() # get list of only unique values in dataColumn
    # dataset lifetime monthly range list for all areas 
    monthRange = pd.date_range(start='01.01.2000', end = '01.01.2025', freq='MS').to_pydatetime()
    xtick_replace= [] # replace select months
    xtick_values = [] # xtick new scale values
    area_allocation = [] #allocates x,y values to area
    ppl.figure() # get all area data
    for area in range(0, len(uniqueArea)):
        x_values = [] # new area needs new x values
        y_values = [] # new area needs new y values
        for i in range(0, len(monthRange)-1): # find count for each area
            x_values.append(str(monthRange[i]))
            if (monthRange[i].month % 12 == 0) and (monthRange[i].year % 2 == 0): # scale for years
                xtick_replace.append(str(monthRange[i]))
                xtick_values.append(str(monthRange[i].year))
            # count incidents for an area and within month range make function
            y_values.append(countInDataRange(dateColumnSeries, cleanedArea, uniqueArea[area], monthRange[i], monthRange[i+1]))
        area_allocation.append([uniqueArea[area],[x_values, y_values]])
        # plot line graph figures
        ppl.plot(area_allocation[area][1][0], area_allocation[area][1][1])
    ppl.xlabel("Timeline")
    ppl.ylabel("Incidents per month")
    ppl.xticks(xtick_replace, xtick_values)
    ppl.savefig("Cartobreach/static/images/continent_incidents_per_month.png")

# function that constructs a pie chart from a dataSeries assume cleaned, a column of unique values
def pieChart(dataColumnSeries):
    # initialize pie chart
    pie = py.Pie()
    pie.title = 'Pie chart'
    # get list of unique values eg. continents (all 7 continent alpha codes)
    uniqueList = []
    for rowList in dataColumnSeries:
        for i in rowList:
            if i not in ["Not available", "N/A"]: # only include actual values
                if i not in uniqueList:
                    uniqueList.append(i)
    # combine whole series into macroList
    macroList = []
    for p in dataColumnSeries:
        macroList.extend(p)
    for iList in uniqueList: # count occurences of unique value in dataColumnSeries
        iCount = macroList.count(iList)
        iCountPercent = round(((float(iCount)/float(len(macroList))) * 100),2)
        pie.add(iList, [{'value':iCount, 'label':str(iCountPercent)+"%"}])
    return pie.render().decode("utf-8")

# function that constructs a bar chart with dataSeries assume cleaned, a column of unique values for different bars
def barChart(dataColumnSeries):
    bar = py.Bar()
    bar.title = "Bar chart"
    # find unique values
    uniqueList = []
    for rowList in dataColumnSeries:
        for i in rowList:
            if i not in ["Not available", "N/A"]: # only include actual values
                if i not in uniqueList:
                    uniqueList.append(i)
    # combine whole series into list
    macroList = []
    for b in dataColumnSeries:
        macroList.extend(b)
    # count occurences of unique value in dataColumnSeries
    for iList in uniqueList: # count occurences of unique value in dataColumnSeries
        iCount = macroList.count(iList)
        bar.add(iList, [iCount])
    return bar.render().decode("utf-8")