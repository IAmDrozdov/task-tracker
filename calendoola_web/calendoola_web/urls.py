from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('caleweb.urls')),
    url('^', include('django.contrib.auth.urls')),
]
