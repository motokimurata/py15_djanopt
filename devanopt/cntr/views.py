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

def frontpage(request):
    if request.method == 'POST':
        print("hello")
        tbl_result = cal_opt(request)
        if tbl_result is not None:
            request.session['tbl_result'] = tbl_result
            return redirect('display_csv')  # リダイレクト
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
            print(tbl_result)
            return tbl_result

            #return display_csv(request, tbl_result=tbl_result)
    errors = form.errors
    print(errors)
    return None

def display_csv(request):
    # セッションから tbl_result を取得
    print(request)
    tbl_result = cal_opt(request)
    print(tbl_result)
    if tbl_result is not None:
            request.session['tbl_result'] = tbl_result
            return HttpResponseRedirect(reverse('display_csv'))

    tbl_result_load = request.session.get('tbl_result', None)
    # データフレーム形式に戻す。
    df_tbl_result = pd.DataFrame(tbl_result_load)   
    tbl_result = df_tbl_result.to_html(index=False, escape=False, header=True)
    
    context = {
        'tbl_result': tbl_result,
    }
    
    return render(request, 'cntr/display_csv.html', context)
        
def download_csv(request):
    # セッションから tbl_result を取得
    tbl_result_load = request.session.get('tbl_result', None)
    if tbl_result_load:
        # データフレーム形式に戻す。
        df_tbl_result = pd.DataFrame(tbl_result_load)

        
        current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"result_csv_{current_datetime}.csv"
        
        # CSVファイルを作成
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df_tbl_result.to_csv(path_or_buf=response, sep=';', float_format='%.2f', index=False, decimal=",")
        
        return response

    return HttpResponse("Invalid Request")

def schedule(request):
    tbl_result_load = request.session.get('tbl_result', None)
    df_tbl_result = pd.DataFrame(tbl_result_load)
    
    # カレンダー用のデータを格納するリスト
    calendar_events = []

    for index, row in df_tbl_result.iterrows():
        event = {
            'title': f"{row['コンテナNo']} - {row['部署名']}",  # イベントのタイトルにコンテナNoと部署名を含む
            'start': row['希望納品日'],  # 希望納品日を開始日とする
            'end': row['希望納品日'],  # 希望納品日を終了日とする（同一日の場合）
            'description': '',  # イベントの説明（オプション）
        }
        calendar_events.append(event)

    # カレンダー用のデータをJSONに変換してテンプレートに渡す
    calendar_events_json = json.dumps(calendar_events)
    
    context = {
        'calendar_events': calendar_events_json,
    }

    template = loader.get_template("cntr/schedule.html")
    return HttpResponse(template.render(context, request))
