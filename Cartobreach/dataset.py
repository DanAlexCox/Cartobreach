import pandas as pd #pip install pandas
import pycountry_convert as pcc #pip install pycountry-convert
from datetime import datetime

#get data from csv
df = pd.read_csv("Cartobreach/csv/eurepoc_global_dataset_1_3.csv", usecols=["incident_id", "name", "incident_type", "start_date", "end_date", "receiver_country", "receiver_country_alpha_2_code"], nrows=5)

#convert dates formatted in DD.MM.YYYY
df["start_date"] = pd.to_datetime(df["start_date"], format="%d.%m.%Y", errors='coerce')
df["end_date"] = pd.to_datetime(df["end_date"], format="%d.%m.%Y", errors='coerce')

#sort by start date
groupStartDate = df.sort_values(by=["start_date"], ascending=True)

#split columns that can have multiple values separated by semicolon into lists
df["incident_type"] = df["incident_type"].str.split(";")
df["receiver_country"] = df["receiver_country"].str.split(";")
df["receiver_country_alpha_2_code"] = df["receiver_country_alpha_2_code"].str.split(";")

#if columns have duplicates in list, remove duplicates by creating a tuple and converting back to list

df["incident_type"] = df["incident_type"].apply(
    lambda x: x if isinstance(x, (list, tuple, str)) else []).apply(lambda x: list(dict.fromkeys(x)))
df["receiver_country"] = df["receiver_country"].apply(
    lambda x: x if isinstance(x, (list, tuple, str)) else []).apply(lambda x: list(dict.fromkeys(x)))
df["receiver_country_alpha_2_code"] = df["receiver_country_alpha_2_code"].apply(
    lambda x: x if isinstance(x, (list, tuple, str)) else []).apply(lambda x: list(dict.fromkeys(x)))

#make new column receiver_continent
df["receiver_continent_code"] = df["receiver_country_alpha_2_code"]

#convert alpha codes to continents
def countryCodeToContinentCode(cellList):
    continents = []
    for code in cellList:
        try:
            contCode = pcc.country_alpha2_to_continent_code(code)
            continents.append(contCode)
        except:
            continents.append("N/A")
    return continents

df["receiver_continent_code"] = df["receiver_continent_code"].apply(countryCodeToContinentCode)

#only unique continent codes allowed
df["receiver_continent_code"] = df["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))
print(df)



