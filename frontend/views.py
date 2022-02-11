from django.shortcuts import render

#take the request and it will simply that HTML to whatever send to request
def index(request, *args, **kwargs):
    return render(request,'frontend/index.html')

