# Class for website

# Class for map
class Map:
    def __init__(self, width, height, x, y):
        self._width = width # width
        self._height = height # height
        self._x = x # x coordinates
        self._y = y # y coordinates
    
    def getWidth(self):
        return self._width # width getter
    
    def setWidth(self, value):
        self._width = value # width setter
        
    def getHeight(self):
        return self._height # height getter
    
    def setHeight(self, value):
        self._height = value # height setter
        
    def getX(self):
        return self._x # x coordinate getter
    
    def setX(self, value):
        self._x = value # x coordinate setter
        
    def getY(self):
        self._y # y coordinate getter
    
    def setY(self, value):
        self._y = value # width setter
        
# Class for continents
class Continent:
    def __init__(self, name, alpha_code, name_map, val=1):
        self._name = name # name of continent
        self._alpha_code = alpha_code # alpha code of continent
        self._name_map = name_map # name on world map
        self._val = val # active value of continent
    
    def getName(self): # name getter
        return self._name 
    
    def setName(self, value): # name setter
        self._name = value
        
    def getAlphaCode(self): # continent alpha code getter
        return self._alpha_code 
    
    def setAlphaCode(self, value): # continent setter
        self._alpha_code = value
        
    def getNameMap(self): # name on map getter
        return self._name_map 
    
    def setNameMap(self, value): # name on map setter
        self._name_map = value
    
    def getValue(self): # active value of continent getter
        return self._val
    
    def setValue(self, value): # active value of continent setter
        self._val = value
    
# Class for countries
class Country:
    def __init__(self, name, alpha_code_up, alpha_code_low, continent, val=1, most_inci='N/A', most_inci_count='N/A', crit_infra_count='N/A',
                 edu_count='N/A', multi_count='N/A'):
        self._name = name # name of country
        self._alpha_code_up = alpha_code_up # alpha 2 code upper case of country
        self._alpha_code_low = alpha_code_low # alpha 2 code lower case of country
        self._continent = continent # assigned continent
        self._val = val # active value on map
        self._most_inci = most_inci # active value of most popular incident type
        self._most_inci_count = most_inci_count # active value of total most popular incident type
        self._crit_infra_count = crit_infra_count # active value of total critical infrastructure receivers
        self._edu_count = edu_count # active value of total education receivers
        self._multi_count = multi_count # active value of total incidents affecting more than current country
    def getName(self):
        return self._name # name getter
    
    def setName(self, value):
        self._name = value # name setter
    
    def getAlphaCodeUp(self):
        return self._alpha_code_up # country upper case alpha code getter
    
    def setAlphaCodeUp(self, value): # country upper case setter
        self._alpha_code_up = value
    
    def getAlphaCodeLow(self):
        return self._alpha_code_low # country lower case alpha code getter
    
    def setAlphaCodeLow(self, value): # country lower case setter
        self._alpha_code_low = value
        
    def getContinent(self):
        return self._continent # continent getter
    
    def setContinent(self, value): # continent setter
        self._continent = value
        
    def getValue(self): # active value of country getter
        return self._val
    
    def setValue(self, value): # active value of country setter
        self._val = value
        
    def getMostInci(self): # active value of country incident type getter
        return self._most_inci
    
    def setMostInci(self, value): # active value of country incident type setter
        self._most_inci = value
        
    def getMostInciCount(self): # active value of country incident type count getter
        return self._most_inci_count
    
    def setMostInciCount(self, value): # active value of country incident type count setter
        self._most_inci_count = value
    
    def getCritInfraCount(self): # active value of country incidents affecting critical infrastructure getter
        return self._crit_infra_count
    
    def setCritInfraCount(self, value): # active value of country incidents affecting critical infrastructure setter
        self._crit_infra_count = value
    
    def getEduCount(self): # active value of country incidents affecting education getter
        return self._edu_count
    
    def setEduCount(self, value): # active value of country incidents affecting education setter
        self._edu_count = value
    
    def getMultiCount(self): # active value of country incidents affecting multiple countries getter
        return self._multi_count
    
    def setMultiCount(self, value): # active value of country incidents affecting multiple countries setter
        self._multi_count = value

# Class for categories with sub types
class Category:
    def __init__(self, cat_type, cat_subtypes):
        self._cat_type = cat_type # category type option
        self._cat_subtypes = cat_subtypes # category subtype options
        
    def getCatType(self): # category type getter
        return self._cat_type
    
    def setCatType(self, value): # category type setter
        self._cat_type = value
        
    def getCatSubType(self): # category subtype getter
        return self._cat_subtypes
    
    def setSubCatType(self, value): # category subtype setter
        self._cat_subtypes = value
    
