from pygal_maps_world.maps import World #install pygal_maps_world via pip
import pycountry as pc
from pycountry_convert.convert_country_alpha2_to_continent_code import country_alpha2_to_continent_code as cc
 # import pycountry-convert
from .classes.classes import Country as Ctry
# make list country objects same as continents.continentList (Name, Alpha code)
countryList = []
for country in pc.countries:
    name = getattr(country,"name")
    
    alphaCode = getattr(country, "alpha_2")
    # some alpha codes havent been assigned continent
    try:
        contCode = cc(alphaCode)
    except KeyError:
        continue
    cy = Ctry(name,alphaCode,contCode)
    countryList.append(cy)