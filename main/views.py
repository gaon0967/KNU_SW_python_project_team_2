from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'main/index.html')

def traffic_accident(request):
    return render(request, 'trafficAccident/mainPage.html')