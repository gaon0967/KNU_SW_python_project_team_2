from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'main/dashboard_3.html')

def dashboard_2(request):
    return render(request, 'main/dashboard_2.html')