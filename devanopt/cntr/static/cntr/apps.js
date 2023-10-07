document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
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
            today: '当月',
            month: '月',
            list: 'リスト'
          }, 
    });

    // FullCalendarの初期化
    calendar.render();
});
