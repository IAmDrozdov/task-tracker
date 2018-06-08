from calelib.crud import Calendoola
from django.http import HttpResponse

db = Calendoola()


def index(request):
    return HttpResponse('+'.join([t.info for t in db.get_tasks()]))
