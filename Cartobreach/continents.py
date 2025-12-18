from .classes.classes import Continent
from pygal_maps_world.maps import SupranationalWorld #install pygal pygal_maps_world via pip
from bs4 import BeautifulSoup # install beautifulsoup4 then install lxml

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
#     singleContinent.add(continentList[i].getName(), [continentList[i].getNameMap()])
#     singleContinent.render_to_file('Cartobreach/static/images/continents_map_'+continentList[i].getNameMap()+'.svg')

# function that creates and renders continent map to file continents map
def renderContinentMap():
    worldmap = SupranationalWorld(title='Continents',show_legend=False) # Create world map
    # adding the continents
    for continents in continentList:
        worldmap.add(
            continents.getName(), {
                continents.getNameMap(): {
                    'value':continents.getValue(),
                    'label':f'{continents.getName()} incidents: {continents.getValue()}',
                    'xlink': f'/{continents.getAlphaCode()}/'
                }
                }
            )
    return worldmap.render().decode("utf-8")
    
    # mark_safe(svg.to_file('static/images/continents_map.svg', x_title="Hover over continent to see incident numbers.")) # render the map in a SVG file
    
# Inject links into SVG
def injectLinks(svg_path, host, areaCodeList):
    # open and read svg
    with open(svg_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")
    # print(soup)
    # assigning continent codes with url string using a dictionary of key-values
    continent_links = {}
    for contObj in areaCodeList:
        continent_links[contObj.getNameMap()] = (f"{host}/"+contObj.getAlphaCode()+"/")

    # make a href
    for path in soup.find_all("path"):
        cls = path.get("class", "")
        for continent, url in continent_links.items():
            
            if continent in cls:
                a = soup.new_tag("a", **{
                        "xlink:href": url,
                        "target": "_self"
                    })
                path.wrap(a)
    # inject <a> into svg
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
