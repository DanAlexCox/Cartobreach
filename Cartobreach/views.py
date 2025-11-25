from django.shortcuts import render

#renders static content
def simple_view(request):
    data = {"content": "Gfg is the best"}
    return render(request, "geeks.html", data)

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

#testing map.html view
def map(request):
    test_variable = "Hello World!"
    #context dictionary variable name : context data
    context ={
        "test_variable": test_variable,
        "another_test" : "My name is daniel",
        "number_test" : 42,
        "number_list" : [1,2,3,4,5],
        
    }
    return render(request, "index.html", context)