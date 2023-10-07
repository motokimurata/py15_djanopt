from django import forms
from datetime import date

class UploadCSVForm(forms.Form):
    WAREHOUSE_CHOICES = [
        ('NE1PL', 'NE1PL'),
        ('NE1SS', 'NE1SS'),
        ('NE1BR', 'NE1BR'),
        ('NE2PL', 'NE2PL'),
        ('NE2SS', 'NE2SS'),
        ('NE2BR', 'NE2BR'),
        ('NW1PL', 'NW1PL'),
        ('NW1SS', 'NW1SS'),
        ('NW1BR', 'NW1BR'),
    ]
    
    warehouse_select = forms.ChoiceField(
        label="倉庫コード:",
        choices=WAREHOUSE_CHOICES,
        initial='NE1PL'
    )
    start_date = forms.DateField(
        label="開始日:",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="終了日:",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    csv_file = forms.FileField(label='CSVファイル')

    def __init__(self, *args, **kwargs):
        super(UploadCSVForm, self).__init__(*args, **kwargs)

        # 開始日の初期値を本日の日付に設定
        self.fields['start_date'].initial = date(2023,8,25)
        #self.fields['start_date'].initial = date.today()
        self.fields['end_date'].initial = date(2023,9,25)
        #self.fields['end_date'].initial = date.today()
        


