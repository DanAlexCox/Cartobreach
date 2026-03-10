# pip install ...
import matplotlib.pyplot as ppl # import pyplot matlablib
import pandas as pd # import pandas
import pycountry_convert as pcc # import pycountry-convert
import pygal as py
from datetime import datetime # import datetime function
from .continents import AF,AN,AS,EU,NA,OC,SA # import continent objects
from . import map

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
    # check if column already has been cleaned
    if column.apply(lambda v: isinstance(v, list)).all():
        cleanedColumn = column
    else:
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

# function that filters every row that does have only value in each row
def filterSingleColumn(dataset, cellList):
    # clean column
    cellList = cleanColumn(cellList)
    return dataset[cellList.apply(lambda x: isinstance(x, list) and len(x) == 1)]

# function that filters every row that doesnt have only value in each row
def filterMultipleColumns(dataset, column):
    # check first row if its a str not a list
    if not isinstance(column.iloc[0], list):
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
def filterDateRange(dataset, dateColumnSeries, min_date, max_date):

    # convert column to datetime
    dates = pd.to_datetime(dateColumnSeries, format="%d.%m.%Y", errors='coerce')

    # convert min/max if strings
    if isinstance(min_date, str):
        min_date = pd.to_datetime(min_date, format="%d.%m.%Y")

    if isinstance(max_date, str):
        max_date = pd.to_datetime(max_date, format="%d.%m.%Y")

    # boolean mask
    mask = (dates >= min_date) & (dates < max_date)

    return dataset.loc[mask]    

# function that adds rows in a date range
def countInDateRange(dataset, dateColumnSeries, min, max):
    dateFiltered = filterDateRange(dataset, dateColumnSeries, min, max)
    return len(dateFiltered.index)

# function that constructs bar plot for yearly incident counts between dataset minimum and maximum date
def yearlyIncidentBarPlot(dataset, startdate='01.01.2020', enddate='01.01.2025'):
    # yearly date range list
    yearRange = pd.date_range(start=startdate, end=enddate, freq='YS').to_pydatetime()
    # date range counts of each year (count up to end of year, end of year)
    bar = py.Bar(title='Total incidents recorded every year', x_title='Timeline',
                            y_title='Number of incidents', x_label_rotation=30)
    x_values = []
    y_values = []
    for i in range(0, len(yearRange)-1):
        x_values.append(str(yearRange[i].year))
        y_values.append(countInDateRange(dataset, dataset['start_date'], yearRange[i], yearRange[i+1]))
    bar.x_labels = x_values
    bar.add ('Total each year', y_values)
    return bar.render().decode("utf-8")

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
    dataFiltered = filterDataRange(dateColumnSeries, dataColumn, value, min, max)
    return len(dataFiltered.index)

# function that orders based on date (ascending/descending)
def orderByDate(dataset, dateColumn, order):
    if not isinstance(dataset, pd.DataFrame):
        return False
    # check input 'order' is either ascending (True) or descending (False) source: https://www.geeksforgeeks.org/python/how-to-sort-a-pandas-dataframe-by-date/
    if order in [True, False]:
        dataset[dateColumn] = convertDateTime(dataset[dateColumn])
        dataset = dataset.sort_values(by=dateColumn, ascending=order)
        return dataset
    else:
        return "Invalid order"     

# function that constructs a line plot with monthly incidents for all cleaned areas (continents/countries)(cleanColumn(...))
def quarterAllAreasIncidentLinePlot(series, filterColumnSeries, legendList, startdate='01.01.2020', enddate='01.01.2025'):
    if not isinstance(legendList, list):
        print("legendlist not a list")
        exit()
    # dataset lifetime monthly range list for all areas 
    monthRange = pd.date_range(start=startdate, end = enddate, freq='3MS').to_pydatetime()
                
    line = py.DateTimeLine(title='Line Chart Quarterly Incidents', x_title='Timeline',show_minor_x_labels=False,
                            y_title='Incidents every 4 months', show_dots=True, x_label_rotation=30,
                            x_value_formatter=lambda dt: str(dt.year),legend_at_bottom = True,
                            legend_at_bottom_columns=20) # Set graph and axis titles
    # get year for start and end date
    startYear = int(startdate.split('.')[-1])
    endYear = int(enddate.split('.')[-1])
    line.x_labels_major = [datetime(year, 1, 1) for year in range(startYear, endYear)]
    for area in range(0, len(legendList)):
        filteredSeries = filterSpecificColumn(series, filterColumnSeries, legendList[area]) # filter by column value eg. EU
        coords_values = []
        for i in range(0, len(monthRange)-1): # find count for each area
            coords_values.append((monthRange[i], countInDateRange(filteredSeries['start_date'], filteredSeries['start_date'],
                                                                    monthRange[i], monthRange[i+1])))
        # plot line graph figures
        line.add(str(legendList[area]), coords_values)
    return line.render().decode("utf-8")

# function that constructs a pie chart from a dataSeries assume cleaned, a column of unique values
def pieChart(dataColumnSeries, titleName='Pie Chart Template'):
    # initialize pie chart
    pie = py.Pie(title= titleName, legend_at_bottom=True, style=map.pygalSideStyle)
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

# function that constructs a pie chart from a dataSeries assume cleaned, a column of unique values chosen from a string list
# TASK FIX PIE CHART
def pieChartSpecific(dataColumnSeries, specificList, titleName='Pie Chart Template'):
    # initialize pie chart
    pie = py.Pie(title= titleName, legend_at_bottom=True, style=map.pygalSideStyle)
    pie.title = 'Pie chart'
    # combine whole series into macroList
    macroList = []
    for p in dataColumnSeries:
        macroList.extend(p)
    for iList in specificList: # count occurences of unique value in dataColumnSeries
        iCount = macroList.count(iList)
        iCountPercent = round(((float(iCount)/float(len(macroList))) * 100),2)
        pie.add(iList, [{'value':iCount, 'label':str(iCountPercent)+"%"}])
    return pie.render().decode("utf-8")

# function that constructs a bar chart with dataSeries assume cleaned, a column of unique values for different bars
def barChart(dataColumnSeries, titleName):
    bar = py.Bar(title=titleName,legend_at_bottom=True, style=map.pygalSideStyle)
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

# function that constructs a bar chart with dataSeries assume cleaned, a column of unique values for different bars chosen from a string list
def barChartSpecific(dataColumnSeries, titleName, specificList):
    bar = py.Bar(title=titleName,legend_at_bottom=True, style=map.pygalSideStyle)
    bar.title = "Bar chart"
    # combine whole series into list
    macroList = []
    for b in dataColumnSeries:
        macroList.extend(b)
    # count occurences of unique value in dataColumnSeries
    for iList in specificList: # count occurences of specified values in dataColumnSeries
        iCount = macroList.count(iList)
        bar.add(iList, [iCount])
    return bar.render().decode("utf-8")