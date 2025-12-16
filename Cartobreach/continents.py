from .classes.classes import Continent
from django.http import HttpResponse
import pygal #install pygal_maps_world via pip

#Constructing continent objects
AF = Continent("Africa", "AF", "africa")
AN = Continent("Antarctica", "AN", "antartica")
AS = Continent("Asia", "AS", "asia")
EU = Continent("Europe", "EU", "europe")
NA = Continent("North America", "NA", "north_america")
OC = Continent("Oceania", "OC", "oceania")
SA = Continent("South America", "SA", "south_america")

# make continent list for getting individual supranationalworld svgs
continentList = [AF, AN, AS, EU, NA, OC, SA]

# render svg images of all continents separately using loop

# for i in range(0, len(continentList)):
#     singleContinent = pygal.maps.world.SupranationalWorld(show_legend=False)
#     singleContinent.force_uri_protocol = 'http'
#     singleContinent.add(continentList[i].getName(), [continentList[i].getNameMap()])
#     singleContinent.render_to_file('Cartobreach/static/images/continents_map_'+continentList[i].getNameMap()+'.svg')

#Create world map
worldmap = pygal.maps.world.SupranationalWorld()

#Set title
worldmap.title = 'Continents'

# adding the continents
worldmap.add(AF.getName(), [(AF.getNameMap())])
worldmap.add(AN.getName(), [(AN.getNameMap())])
worldmap.add(AS.getName(), [(AS.getNameMap())])
worldmap.add(EU.getName(), [(EU.getNameMap())])
worldmap.add(NA.getName(), [(NA.getNameMap())])
worldmap.add(SA.getName(), [(SA.getNameMap())])
worldmap.add(OC.getName(), [(OC.getNameMap())])

#render the map in a SVG file
# worldmap.render_to_file('Cartobreach/static/images/continents_map.svg')
