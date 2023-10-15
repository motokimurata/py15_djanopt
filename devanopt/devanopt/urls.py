from django.contrib import admin
from django.urls import path
from cntr.views import frontpage
from cntr.views import download_excel
from cntr.views import schedule
from cntr.views import warehouse_capacity
from cntr.views import delete_records
from cntr.views import warehouse_csv_upload




urlpatterns = [
    path('admin/', admin.site.urls),
    path("", frontpage),
    path('download_csv/', download_excel, name='download_csv'),
    path('sc/', schedule, name='schedule'),
    path('wh/', warehouse_capacity, name='warehouse_capacity'),
    path('delete_records/', delete_records, name='delete_records'),
    path('warehouse_csv_upload/', warehouse_csv_upload, name='warehouse_csv_upload'),



]


