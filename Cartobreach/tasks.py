from . import dataset
ds = dataset.df


# total incidents
totalIncidents = len(ds.index)

# count how many attacks were towards corporate industry
corporateAttacks = dataset.countUncleanColumnValues("receiver_category", "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)")

# count how many attacks were towards military
militaryAttacks = dataset.countUncleanColumnValues("receiver_subcategory","Military")

# # sort by start date
# df.sort_values(by=["start_date"], ascending=True)

# # make new column receiver_continent with unique values only
# df["receiver_country_alpha_2_code"] = cleanColumn("receiver_country_alpha_2_code")
# df["receiver_continent_code"] = df["receiver_country_alpha_2_code"].apply(convertCountryCodeToContinentCode)
# df["receiver_continent_code"] = df["receiver_continent_code"].apply(lambda x: list(dict.fromkeys(x)))

# # count how many attacks occured relating political groups/governments in a continent
# countUncleanDoubleColumnValues("receiver_category","State institutions / political system","receiver_continent_code",NA.getAlphaCode())

# # count how many attacks occured relating to social groups in a continent
# countUncleanDoubleColumnValues("receiver_category","Social groups","receiver_continent_code",NA.getAlphaCode())

# # count how many attacks occured relating to critical infrastrastructure in a continent
# countUncleanDoubleColumnValues("receiver_category","Critical infrastructure","receiver_continent_code",AS.getAlphaCode())

# # filter list so it includes only known start and end dates
# filterDateTime(df["start_date"])
# filterDateTime(df["end_date"])

# # make df series only with one singular type of incident
# filterSingleColumn("incident_type")

# # make df series only with more than one type of incident
# filterMultipleColumns("incident_type")

# # filter df series for one type of incident
# filterSpecificColumn("incident_type","Data_theft")

# # filter df series using two column conditions
# filterTwoColumns("incident_type", "Disruption", "receiver_continent_code", NA.getAlphaCode())

# # total intensity weight for an area alpha code (data_theft, disruption, hijacking, physical_effects_spatial, physical_effects_temporal, unweighted_intensity)
# totalAreaIntensity("receiver_continent_code", AS.getAlphaCode())

# # intensity of an area filtering to a column value
# totalMultipleIntensity("incident_type", "Data theft", "receiver_continent_code", EU.getAlphaCode())

# # intensity of an area alpha code broken down into data_theft, "disruption", "hijacking", "physical_effects_spatial", "physical_effects_temporal"
# specificIntensity("data_theft", "receiver_continent_code", NA.getAlphaCode())

# # count how many instances of known functional disruption are there in a region
# countUncleanDoubleColumnValues("functional_impact", "Days (< 7 days)", "receiver_continent_code", SA.getAlphaCode())

# # count how many instances of known intelligence disruption are there in a region
# countUncleanDoubleColumnValues("intelligence_impact", "Minor data breach/exfiltration (no critical/sensitive information), data corruption (deletion/altering) and/or leaking of data  ", "receiver_continent_code", AS.getAlphaCode())

# # convert initiator country code to continent code
# df["initiator_continent_code"] = cleanColumn("initiator_alpha_2")
# df["initiator_continent_code"] = df["initiator_continent_code"].apply(convertCountryCodeToContinentCode)
# df["initiator_continent_code"] = df["initiator_continent_code"].apply(lambda x: list(dict.fromkeys(x)))

# # count initiators from region
# countUncleanColumnValues("initiator_continent_code", AS.getAlphaCode())

# # count initiators from region that attacked corporate targets
# countUncleanDoubleColumnValues("receiver_category", "Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)", "initiator_continent_code", NA.getAlphaCode())

# # set continent values
# AF.setValue(countUncleanColumnValues("receiver_continent_code", AF.getAlphaCode())),
# AS.setValue(countUncleanColumnValues("receiver_continent_code", AS.getAlphaCode()))
# AN.setValue(countUncleanColumnValues("receiver_continent_code", AN.getAlphaCode()))
# EU.setValue(countUncleanColumnValues("receiver_continent_code", EU.getAlphaCode()))
# NA.setValue(countUncleanColumnValues("receiver_continent_code", NA.getAlphaCode()))
# OC.setValue(countUncleanColumnValues("receiver_continent_code", OC.getAlphaCode()))
# SA.setValue(countUncleanColumnValues("receiver_continent_code", SA.getAlphaCode()))

# # bar plot for instances in each continent
# barValues = [countUncleanColumnValues("receiver_continent_code", AF.getAlphaCode()),
#              countUncleanColumnValues("receiver_continent_code", AS.getAlphaCode()),
#              countUncleanColumnValues("receiver_continent_code", AN.getAlphaCode()),
#              countUncleanColumnValues("receiver_continent_code", EU.getAlphaCode()),
#              countUncleanColumnValues("receiver_continent_code", NA.getAlphaCode()),
#              countUncleanColumnValues("receiver_continent_code", OC.getAlphaCode()),
#              countUncleanColumnValues("receiver_continent_code", SA.getAlphaCode())]
# barNames = [AF.getName(), AS.getName(), AN.getName(), EU.getName(), NA.getName(), OC.getName(), SA.getName()]

# ppl.figure()
# ppl.bar(barNames, barValues, color="blue")
# ppl.xlabel("Continents")
# ppl.xticks(fontsize=8)
# ppl.ylabel("No. of Incidents")
# # ppl.savefig("Cartobreach/static/images/continent_incidents.png")

# # line graph to show number of incidents every year i.e. known start date range 1/1/2000 <= x < 1/1/2025
# yearlyIncidentLinePlot(df["start_date"], '01.01.2000', '01.01.2025')
# # line graph to show all continents' total incidents each month each with different colours
# monthlyAllAreasIncidentLinePlot(df["start_date"], df["receiver_continent_code"])
