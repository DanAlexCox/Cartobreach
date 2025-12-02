from classes.classes import Continent
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

worldfile = worldmap.render_to_file('Cartobreach/static/images/continents_map.svg')
