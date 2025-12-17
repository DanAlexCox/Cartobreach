from .classes.classes import Continent
from django.http import HttpResponse
from pygal_maps_world.maps import SupranationalWorld #install pygal pygal_maps_world via pip

#Constructing continent objects
AF = Continent("Africa", "AF", "africa")
AN = Continent("Antartica", "AN", "antartica")
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
worldmap = SupranationalWorld(show_legend = False)

#Set title
worldmap.title = 'Continents'

# adding the continents
for continents in continentList:
    worldmap.add(continents.getName(), [(continents.getNameMap())])

#render the map in a SVG file
rendermap = worldmap.render_to_file('static/images/continents_map.svg')
