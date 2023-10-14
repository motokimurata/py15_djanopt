from django.contrib import admin
from django.urls import path
from cntr.views import frontpage
from cntr.views import download_csv
from cntr.views import schedule


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", frontpage),
    path('download_csv/', download_csv, name='download_csv'),
    path('sc/', schedule, name='schedule'),


]


