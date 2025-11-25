from classes.classes import Continent
from django.http import HttpResponse
import pygal #install pygal_maps_world via pip


#Constructing continent objects
AF = Continent("Africa", "africa", "yellow")
AN = Continent("Antarctica", "antartica", "white")
AS = Continent("Asia", "asia", "red")
EU = Continent("Europe", "europe", "blue")
NA = Continent("North America", "north_america", "green")
OC = Continent("Oceania", "oceania", "purple")
SA = Continent("South America", "south_america", "orange")


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
