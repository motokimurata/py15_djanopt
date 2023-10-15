from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import UploadCSVForm
import os
import pandas as pd
from .models import WarehouseCapacity
from .devan_opt import optimize_delivery_schedule
from django.urls import reverse
import json
from datetime import datetime
from django.template import loader
from cntr.models import WarehouseCapacity
from .forms import WarehouseCapacityFilterForm
from .forms import WarehouseUploadCSVForm

import csv

def frontpage(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['csv_file']
            if uploaded_file.name.endswith('.csv'):
                tbl_result = cal_opt(request)
                if tbl_result is not None:
                    request.session['tbl_result'] = tbl_result
                return HttpResponseRedirect(reverse('schedule'))
    else:
        form = UploadCSVForm()
    return render(request, 'cntr/frontpage.html', {'form': form})

def cal_opt(request):
    form = UploadCSVForm(request.POST, request.FILES)
    if form.is_valid():
        csv_file = request.FILES['csv_file']
        if csv_file.name.endswith('.csv'):
            table1 = pd.read_csv(csv_file)
            date_filter_start = form.cleaned_data['start_date']
            date_filter_end = form.cleaned_data['end_date']
            target = form.cleaned_data['warehouse_select']

            # WarehouseCapacityモデルからデータを取得
            data = WarehouseCapacity.objects.filter(warehouse_code=target, date__range=[date_filter_start, date_filter_end]).order_by('date')

            # 取得したデータをPandas DataFrameに変換
            df = pd.DataFrame(list(data.values()))

            # tbl3の変換ロジックを実行
            table3_org = df.pivot(index='date', columns='warehouse_code', values='capacity').fillna(0).reset_index()

            # 日付の若い順に並び替え
            table3 = table3_org.copy()
            table3['date'] = pd.to_datetime(table3['date'])
            table3 = table3.sort_values(by='date')
            tbl_temp_result = optimize_delivery_schedule(date_filter_start, date_filter_end, table1, target,table3)
            tbl_temp_result['入港日'] = tbl_temp_result['入港日'].dt.strftime('%Y-%m-%d')
            tbl_temp_result['希望納品日'] = tbl_temp_result['希望納品日'].dt.strftime('%Y-%m-%d')
            tbl_temp_result['最適納品日'] = tbl_temp_result['最適納品日'].apply(lambda x: x.strftime('%Y-%m-%d'))
            tbl_result=tbl_temp_result.to_dict()
            return tbl_result

            #return display_csv(request, tbl_result=tbl_result)
    errors = form.errors
    print(errors)
    return None
        
def download_excel(request):
    # セッションから tbl_result を取得
    tbl_result_load = request.session.get('tbl_result', None)
    if tbl_result_load:
        # データフレーム形式に戻す
        df_tbl_result = pd.DataFrame(tbl_result_load)

        # 現在の日時を取得してフォーマット
        current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')

        # ファイル名に日時を追加してExcel形式でダウンロードするためのHttpResponseを生成
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="result_excel_{current_datetime}.xlsx'

        # データフレームをExcel形式に変換してHttpResponseに書き込み
        df_tbl_result.to_excel(response, index=False, engine='openpyxl')

        return response

    return HttpResponse("Invalid Request")

def schedule(request):
    tbl_result_load = request.session.get('tbl_result', None)
    df_tbl_result = pd.DataFrame(tbl_result_load)

    # カレンダー用のデータを格納するリスト
    calendar_events = []

    for index, row in df_tbl_result.iterrows():
        # 希望納品日を文字列からJavaScriptのDateオブジェクトに変換
        start_date = row['最適納品日']

        event = {
            'title': f"{row['部署']} - {row['コンテナ番号']}",  # イベントのタイトルにコンテナNoと部署名を含む
            'start': start_date,  # 希望納品日をJavaScriptのDateオブジェクトとして設定
            'end': start_date,  # 希望納品日を終了日とする（同一日の場合）
            'description': '',  # イベントの説明（オプション）
            'color': 'red',  # イベントの背景色を赤に設定
            'extendedProps': {  # カスタムプロパティを追加
                'container_number': row['コンテナ番号'],
                'department': row['部署'],
                'warehouse': row['納入倉庫'],
                'arrival_date': row['入港日'],
                'desired_delivery_date': row['希望納品日'],
                'optimal_delivery_date': row['最適納品日'],
            }
        }
        calendar_events.append(event)

    # カレンダー用のデータをJSONに変換してテンプレートに渡す
    calendar_events_json = json.dumps(calendar_events)

    context = {
        'calendar_events': calendar_events_json,
    }

    template = loader.get_template("cntr/schedule.html")
    return HttpResponse(template.render(context, request))

def warehouse_capacity(request):
    form = WarehouseCapacityFilterForm(request.GET)
    capacities = WarehouseCapacity.objects.all()  # データベースから全てのキャパシティ情報を取得
    if form.is_valid():
        warehouse_code = form.cleaned_data.get('warehouse_code')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if warehouse_code:
            capacities = capacities.filter(warehouse_code=warehouse_code)
        if start_date:
            capacities = capacities.filter(date__gte=start_date)
        if end_date:
            capacities = capacities.filter(date__lte=end_date)

    return render(request, 'warehouse_capacity.html', {'form': form, 'capacities': capacities})

def delete_records(request):
    if request.method == 'POST':
        record_ids = request.POST.getlist('record_id')
        WarehouseCapacity.objects.filter(id__in=record_ids).delete()
        return redirect('warehouse_capacity')  # 削除後、倉庫キャパシティページにリダイレクト
    return redirect('warehouse_capacity')

def warehouse_csv_upload(request):
    error_message = ""  # エラーメッセージを初期化
    if request.method == 'POST':
        upload_csv_form = WarehouseUploadCSVForm(request.POST, request.FILES)
        if upload_csv_form.is_valid():
            csv_file = request.FILES['csv_file']
            if csv_file.name.endswith('.csv'):
                data = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(data)
                next(reader)  # Skip the header row
                for row in reader:
                    warehouse_code, date_str, capacity_str = row
                    date = datetime.strptime(date_str, '%Y/%m/%d').date()
                    capacity = int(capacity_str)
                    # ユニークな条件を確認し、データベースに追加
                    if WarehouseCapacity.objects.filter(warehouse_code=warehouse_code, date=date).count() == 0:
                        WarehouseCapacity.objects.create(warehouse_code=warehouse_code, date=date, capacity=capacity)
                
                # 成功時に warehouse_capacity ページにリダイレクト
                return redirect('warehouse_capacity')
            else:
                error_message = "Invalid file format. Please upload a valid CSV file."
        else:
            error_message = "Form is not valid. Please check your file and try again."
    else:
        upload_csv_form = WarehouseUploadCSVForm()
    return render(request, 'warehouse_capacity_upload.html', {'upload_csv_form': upload_csv_form, 'error_message': error_message})