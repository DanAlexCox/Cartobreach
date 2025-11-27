from django.shortcuts import render
from django import template

#register library for templates
register = template.Library()

#handles form input and applies conditional rendering.
def check_age(request):
    age = None
    if request.method == 'POST':
        # request.POST.get returns a string, default to "0"
        age = int(request.POST.get('age', 0))
    return render(request, 'check_age.html', {'age': age})

#passes a list and string to demonstrate looping and filters.
def loop(request):
    data = "Gfg is the best"
    number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    context = {
        "data": data,
        "list": number_list
    }
    return render(request, "loop.html", context)

#returns variable type
@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__

#testing map.html view
def map(request):
    mapload = None
    #post check post method
    if request.method == 'POST':
        #returns mapload if submit button 'maploader' is clicked
        mapload = request.POST.get('mapload', None)
    
    #content dictionary
    context = {
        'index' : "",
        'map' : "map.html",
        'mapload' : mapload,
    }

    return render(request, "index.html", context)