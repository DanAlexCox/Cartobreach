from pygal_maps_world.i18n import COUNTRIES # install pygal_maps_world
from pygal_maps_world.maps import World #install pygal_maps_world via pip
import pycountry as pc
from pycountry_convert.convert_country_alpha2_to_continent_code import country_alpha2_to_continent_code as cc
 # import pycountry-convert
from .classes.classes import Country

# make list country objects same as continents.continentList (Name, Alpha code)
countryList = []

# construct country class objects then add to countryList
for code, name in COUNTRIES.items():
    country = Country(name, code.upper(), code.lower())
    countryList.append(country)
    
# function that creates and renders country map
def renderCountryMap():
    worldmap = World(title='Countries')
    # add the countries to map
    for countrys in countryList:
        worldmap.add(
            countrys.getName(), {countrys.getAlphaCodeLow():countrys.getValue()}
        )
    return worldmap.render().decode("utf-8")