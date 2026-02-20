from pygal_maps_world.i18n import COUNTRIES # install pygal_maps_world
from pygal_maps_world.maps import World #install pygal_maps_world via pip
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
    
# function that creates and renders country map
def renderCountryMap(total_value):
    worldmap = World(title='Countries', legend_at_bottom = True, legend_at_bottom_columns=20, style=map.totalIncidentStyle, print_labels=True)
    # add the countries to map
    for countrys in countryList:
        colour = map.styleColours(countrys.getValue(),total_value,255,0,0)
        # TASK NOT FINISHED DYNAMIC COLOURING
        worldmap.add(
            countrys.getAlphaCodeUp(), [{
                'value': (countrys.getAlphaCodeLow(),
                          '\nTotal number of incidents - '+str(countrys.getValue())
                          +'\nNew line'
                          ),
                'color' : colour,
                'xlink': f'/country/{countrys.getName()}/'  # LINK WORKS solution: https://github.com/Kozea/pygal/issues/173
            }]
        )
    return worldmap.render().decode("utf-8")