document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar'); // カレンダーを表示する要素を取得
    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'ja',
        firstDay: 1,
        headerToolbar: {
            left: "dayGridMonth,listMonth",
            center: "title",
            right: "today prev,next"
          },
        height: 'auto', // カレンダーの高さを自動調整
        buttonText: {
            today: '今月',
            month: '月',
            list: 'リスト'
          },    
    });

    // FullCalendarの初期化
    calendar.render();
});
