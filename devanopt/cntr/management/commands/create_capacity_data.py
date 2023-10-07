import csv
from datetime import datetime
from cntr.models import WarehouseCapacity
from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Create capacity data from CSV'

    def handle(self, *args, **options):
        # 初期化処理を追加
        connections.close_all()
        
        with open('warehouse_db.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                warehouse_code, date_str, capacity_str = row
                date = datetime.strptime(date_str, '%Y/%m/%d').date()
                capacity = int(capacity_str)
                WarehouseCapacity.objects.create(warehouse_code=warehouse_code, date=date, capacity=capacity)
        self.stdout.write(self.style.SUCCESS('Capacity data created successfully'))