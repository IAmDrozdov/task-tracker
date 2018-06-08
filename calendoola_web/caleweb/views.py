from django.http import HttpResponse
from calelib.crud import Calendoola
db = Calendoola()


def index(request):
    return HttpResponse('+'.join([t.info for t in db.get_tasks()]))
