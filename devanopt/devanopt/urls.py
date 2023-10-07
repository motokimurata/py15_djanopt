from django.contrib import admin
from django.urls import path
from cntr.views import frontpage
from cntr.views import display_csv
from cntr.views import download_csv
from cntr.views import schedule


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", frontpage),
    path('display_csv/', display_csv, name='display_csv'),  # CSVアップロード用のURL
    path('download_csv/', download_csv, name='download_csv'),

]


