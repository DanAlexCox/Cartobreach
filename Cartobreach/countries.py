from pygal_maps_world.i18n import COUNTRIES # install pygal_maps_world
from pygal_maps_world.maps import World 
from urllib.parse import urlencode
from . import map
from .classes.classes import Country
import pycountry_convert as pc # import pycountry-convert

# function that converts a countries alpha 2 code into continent name
def countryalpha2_to_continent(country_alpha2):
    if country_alpha2 == 'AQ': # causes error trying to convert Antarctica
        return 'Antarctica'
    elif country_alpha2 == 'EH': # causes error trying to convert Western Sahara
        return 'Africa'
    elif country_alpha2 == 'TL': # causes error trying to convert Timor-Leste
        return 'Asia'
    elif country_alpha2 == 'VA': # causes error trying to convert Vatican City
        return 'Europe'
    else:
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return pc.convert_continent_code_to_continent_name(continent_code)
# make list country objects same as continents.continentList (Name, Alpha code)
countryList = []
# construct country class objects then add to countryList
for code, name in COUNTRIES.items():
    country = Country(name, code.upper(), code.lower(), countryalpha2_to_continent(code.upper()))
    countryList.append(country)
    
# function that creates and renders country map with links that add specific country to current parameters e.g. after filter form get params
def renderCountryMap(total_value, getfullpath, lastKnownName = 'N/A', lastDate = 'N/A'):
    # layout for map
    worldmap = World(title='Countries', legend_at_bottom = True, legend_at_bottom_columns=20, style=map.totalIncidentStyle, print_labels=True)
    # colorList = []
    # add the countries to map
    for countrys in countryList:
        # colour = map.styleColours(countrys.getValue(),total_value,255,0,0) # get hex code from value
        # colorList.append(colour) # add hex code into color list
        
        # task optional if have time on top of report/presentation: fix monotonic colour scheme
        # if parameters are int, collect percentage with respect to getValue() (total incidents with respect to total_value)
        totalPerc = countrys.getValue()/total_value * 100 if isinstance(total_value, int) else 'N/A'
        typePerc = countrys.getMostInciCount()/countrys.getValue() * 100 if isinstance(countrys.getMostInciCount(), int) else 'N/A'
        critInfraPerc = countrys.getCritInfraCount()/countrys.getValue() * 100 if isinstance(countrys.getCritInfraCount(), int) else 'N/A'
        eduPerc = countrys.getEduCount()/countrys.getValue() * 100 if isinstance(countrys.getEduCount(), int) else 'N/A'
        multiPerc = countrys.getMultiCount()/countrys.getValue() * 100 if isinstance(countrys.getMultiCount(), int) else 'N/A'
        worldmap.add(
            countrys.getAlphaCodeUp(), [{
                # value represents information displayed in the hoverover box "tooltip"
                'value': (countrys.getAlphaCodeLow(),
                          '\nTotal number of incidents - '+str(countrys.getValue())+' ('+str(totalPerc)+'% of the filtered data)'
                          +'\nIncident type occurring the most - '+str(countrys.getMostInci())+' ('+str(typePerc)+'% of the filtered country data)' # most occurences of an incident type
                          +'\nNumber of incidents affecting critical infrastructure - '+str(countrys.getCritInfraCount())+ ' ('+str(critInfraPerc)+'% of the filtered country data)'    # count critical infrastructure
                          +'\nNumber of incidents affecting education - '+str(countrys.getEduCount())+ ' ('+str(eduPerc)+'% of the filtered country data)'   # count education
                          +'\nNumber of incidents affecting more than this country - '+str(countrys.getMultiCount())+ ' ('+str(multiPerc)+'% of the filtered country data)'    # count only >1 country in receiver country
                          +'\nLast known incident - '+str(lastKnownName)+' (dated: '+str(lastDate)+')'  # most recent incident "name" and "start date" 
                          ),
                
                # 'color' : colour,
                # xlink represents directory going to once series is clicked
                'xlink': f"{getfullpath}&{urlencode({'country':countrys.getAlphaCodeUp()})}"  # LINK WORKS solution: https://github.com/Kozea/pygal/issues/173
            }]
        )
    return worldmap.render().decode("utf-8")