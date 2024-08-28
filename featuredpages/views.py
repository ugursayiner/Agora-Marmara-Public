from django.shortcuts import render

# Create your views here.
def open_frontpage(request):
    return render(request, 'frontpage.html')