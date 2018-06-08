from calelib.crud import Calendoola
from django.shortcuts import render
db = Calendoola()


def index(request):
    return render(request, 'caleweb/homePage.html')
