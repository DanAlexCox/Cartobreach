import pandas as pd #pip install pandas
import pycountry_convert as pcc #pip install pycountry-convert
from datetime import datetime
from continents import AF,AN,AS,EU,NA,OC,SA #importing continent objects

#get data from csv
df = pd.read_csv("Cartobreach/csv/eurepoc_global_dataset_1_3.csv", usecols=["incident_id", "name", "incident_type", "start_date", "end_date", "receiver_country_alpha_2_code", "receiver_category", "receiver_subcategory"], nrows=5)

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
def countUncleanColumnValuesInContinent(column, search, alsocolumn, alsosearch):
    #clean columns
    cleanedColumn = cleanColumn(column)
    cleanedAlsoColumn = cleanColumn(alsocolumn)

    return cleanedColumn.apply(lambda x: (
         isinstance(x, list)
         and search in x
         and isinstance(cleanedAlsoColumn, list)
         and alsosearch in cleanedAlsoColumn
        ), axis=1).sum()

# convert start and end dates
df["start_date"] = df["start_date"].apply(convertDateTime)
df["end_date"] = df["end_date"].apply(convertDateTime)

#sort by start date
groupStartDate = df.sort_values(by=["start_date"], ascending=True)

# make new column receiver_continent with unique values only
df["receiver_country_alpha_2_code"] = cleanColumn("receiver_country_alpha_2_code")
df["receiver_continent_code"] = df["receiver_country_alpha_2_code"].apply(convertCountryCodeToContinentCode)
df["receiver_continent_code"] = df["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
    
# count how many attacks were towards corporate industry
print(countUncleanColumnValues("receiver_category", "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)"))

# count how many attacks were towards military
print(countUncleanColumnValues("receiver_subcategory","Military"))

# count how many attacks occured relating political groups/governments in a continent
print(countUncleanColumnValuesInContinent("receiver_category","State institutions / political system","receiver_continent_code",NA.getAlphaCode()))

