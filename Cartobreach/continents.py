from .classes.classes import Continent
from pygal_maps_world.maps import SupranationalWorld # install pygal pygal_maps_world via pip
from urllib.parse import urlencode
from textwrap import wrap
from . import map

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
def renderContinentMap(total_value, getfullpath):
    # style colour of map
    worldmap = SupranationalWorld(title='Continents', legend_at_bottom=True, legend_box_size = 10,style=map.totalIncidentStyle, print_labels=True) # Create world map
    # adding the continents
    for continents in continentList:
        # if parameters are int, collect percentage with respect to getValue() (total incidents with respect to total_value)
        totalPerc = continents.getValue()/total_value * 100 if isinstance(total_value, int) else 'N/A'
        typePerc = continents.getMostInciCount()/continents.getValue() * 100 if isinstance(continents.getMostInciCount(), int) else 'N/A'
        critInfraPerc = continents.getCritInfraCount()/continents.getValue() * 100 if isinstance(continents.getCritInfraCount(), int) else 'N/A'
        eduPerc = continents.getEduCount()/continents.getValue() * 100 if isinstance(continents.getEduCount(), int) else 'N/A'
        multiPerc = continents.getMultiCount()/continents.getValue() * 100 if isinstance(continents.getMultiCount(), int) else 'N/A'
        
        # if recent name is longer that 100 character split
        nameList = []
        if len(continents.getRecentName()) > 100:
            nameList = wrap(continents.getRecentName(),100) # help from: https://stackoverflow.com/a/48860937
        else:
            nameList.append(continents.getRecentName())
        
        nameString =''
        # construct name split for tooltip
        for namePart in nameList:
            nameString += str(namePart) +'\n'
        
        worldmap.add(
            continents.getName(), [{
                'value' : (continents.getNameMap(),
                          '\nTotal number of incidents - '+str(continents.getValue())+' ('+str(totalPerc)+'% of the filtered data)'
                          +'\nIncident type occurring the most - '+str(continents.getMostInci())+' ('+str(typePerc)+'% of the filtered continent data)' # most occurences of an incident type
                          +'\nNumber of incidents affecting critical infrastructure - '+str(continents.getCritInfraCount())+ ' ('+str(critInfraPerc)+'% of the filtered continent data)'    # count critical infrastructure
                          +'\nNumber of incidents affecting education - '+str(continents.getEduCount())+ ' ('+str(eduPerc)+'% of the filtered continent data)'   # count education
                          +'\nNumber of incidents affecting more than this continent - '+str(continents.getMultiCount())+ ' ('+str(multiPerc)+'% of the filtered continent data)'    # count only >1 continent in receiver continent
                          +'\nLast known incident:\n'
                          + '- '+nameString # most recent incident "name" 
                          +'- Dated: '+str(continents.getRecentDate())  # most recent incident "start date" 
                          ),
                'xlink' :f"{getfullpath}&{urlencode({'continent':continents.getAlphaCode()})}"  # LINK WORKS solution: https://github.com/Kozea/pygal/issues/173
            }]
        )
    return worldmap.render().decode("utf-8")

