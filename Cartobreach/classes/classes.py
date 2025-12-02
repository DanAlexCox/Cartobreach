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
    def __init__(self, name, alpha_code, name_map):
        self._name = name # name of continent
        self._alpha_code = alpha_code # alpha code of continent
        self._name_map = name_map # name on world map
    
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
    
    
# Class for countries
class Country:
    def __init__(self, name, color):
        self._name = str(name) # name of country
        self._color = str(color) # color of country
    
    def getName(self):
        self._name # name getter
    
    def setName(self, value):
        self._name = value # name setter
        
    def getColor(self):
        self._color # color getter
        
    def setColor(self, value):
        self._color = value # color setter

# Class for scaling continents

# Class for scaling countries

# Class for filter
