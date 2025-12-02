import pandas as pd #pip install pandas
import pycountry_convert as pcc #pip install pycountry-convert
from datetime import datetime
from continents import AF,AN,AS,EU,NA,OC,SA #importing continent objects

#get data from csv
df = pd.read_csv("Cartobreach/csv/eurepoc_global_dataset_1_3.csv", usecols=["incident_id", "name", "incident_type", "start_date", "end_date", "receiver_country_alpha_2_code", "receiver_category", "receiver_subcategory"], nrows=20)

# function that converts date formatted in DD.MM.YYYY
def convertDateTime(column):
    return pd.to_datetime(column, format="%d.%m.%Y", errors ='coerce')

# function that cleans and returns column
def cleanColumn(column):
    #turn into uncleaned column lists
    countList = df[column].str.split(";")
    #clean column lists to make unique values only
    return countList.apply(lambda x: x if isinstance(x, (list, tuple, str)) else x).apply(lambda x: list(dict.fromkeys(x)))

# function for counting how many instances are in an uncleaned column
def countUncleanColumnValues(column, search):
    #clean column and turn into list
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
    count = 0
    for i in df[column]:
        for j in df[alsocolumn]:
            if search in i and alsosearch in j:
                count =count+1
    return count

# function that filters out date type columns to exclude any non date times
def filterDateTime(series):
    # convert to DateTime
    series = series.apply(convertDateTime)
    return series[series.apply(lambda x: isinstance(x, datetime))]

# function that filters every row that doesnt have only value in each row
def filterSingleColumn(cellList):
    #clean column
    cellList = cleanColumn(cellList)
    return df[cellList.apply(lambda x: isinstance(x, list) and len(x) == 1)]

# function that filters every row that doesnt have only value in each row
def filterMultipleColumns(column):
    #clean column
    column = cleanColumn(column)
    return df[column.apply(lambda x: isinstance(x, list) and len(x) > 1)]

# function that filters a specific value from series
def filterSpecificColumn(column, value):
    #clean column
    column = cleanColumn(column)
    return df[column.apply(lambda x: isinstance(x, list) and (value in x))]

#function that calculates total intensity of a region (continent/country)
def totalAreaIntensity(area):
    return area[helo]
    
#sort by start date
groupStartDate = df.sort_values(by=["start_date"], ascending=True)

# make new column receiver_continent with unique values only
df["receiver_country_alpha_2_code"] = cleanColumn("receiver_country_alpha_2_code")
df["receiver_continent_code"] = df["receiver_country_alpha_2_code"].apply(convertCountryCodeToContinentCode)
df["receiver_continent_code"] = df["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    
# count how many attacks were towards corporate industry
countUncleanColumnValues("receiver_category", "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)")

# count how many attacks were towards military
countUncleanColumnValues("receiver_subcategory","Military")

# count how many attacks occured relating political groups/governments in a continent
countUncleanDoubleColumnValues("receiver_category","State institutions / political system","receiver_continent_code",NA.getAlphaCode())

# count how many attacks occured relating to social groups in a continent
countUncleanDoubleColumnValues("receiver_category","Social groups","receiver_continent_code",NA.getAlphaCode())

# count how many attacks occured relating to critical infrastrastructure in a continent
countUncleanDoubleColumnValues("receiver_category","Critical infrastructure","receiver_continent_code",NA.getAlphaCode())

# filter list so it includes only known start and end dates
filterDateTime(df["start_date"])
filterDateTime(df["end_date"])

# make df series only with one singular type of incident
filterSingleColumn("incident_type")

# make df series only with more than one type of incident
filterMultipleColumns("incident_type")

# filter df series for one type of incident
filterSpecificColumn("incident_type","Disruption")

# total intensity weight for an area (date_theft, disruption, hijacking, physical_effects_spatial, physical_effects_temporal, unweighted_intensity)
totalAreaIntensity(AS.getAlphaCode)
