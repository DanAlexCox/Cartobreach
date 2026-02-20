from .classes.classes import Continent
from pygal_maps_world.maps import SupranationalWorld # install pygal pygal_maps_world via pip
from bs4 import BeautifulSoup # install beautifulsoup4 then install lxml

# constructing continent class objects
AF = Continent("Africa", "AF", "africa")
AN = Continent("Antartica", "AN", "antartica")
AS = Continent("Asia", "AS", "asia")
EU = Continent("Europe", "EU", "europe")
NA = Continent("North America", "NA", "north_america")
OC = Continent("Oceania", "OC", "oceania")
SA = Continent("South America", "SA", "south_america")

# make continent list for getting individual supranationalworld svgs
continentList = [AF, AN, AS, EU, NA, OC, SA]

# function that creates and renders continent map
def renderContinentMap():
    worldmap = SupranationalWorld(title='Continents') # Create world map
    # adding the continents
    for continents in continentList:
        worldmap.add(
            continents.getName(), [{
                'value' : (continents.getNameMap(), continents.getValue()),
                'label': 'Total number of incidents',
                'xlink' :f'/continent/{continents.getNameMap()}/'
            }]
        )
    return worldmap.render().decode("utf-8")

