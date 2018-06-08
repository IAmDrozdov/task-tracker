from django.http import HttpResponse
from calelib.crud import Calendoola
db = Calendoola()
db.current_user = 'default'


def index(request):
    return HttpResponse('+'.join([t.info for t in db.get_tasks()]))
