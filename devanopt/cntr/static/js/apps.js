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
      height: 'auto',
      buttonText: {
          today: '当月',
          month: '月',
          list: 'リスト'
      },
      events: calendarEventsData,  // Djangoテンプレートから渡されたデータを使用
      eventClick: function(info) {
          var event = info.event;
          var modal = document.getElementById('eventModal');
          var modalTitle = document.getElementById('eventModalTitle');
          var modalContent = document.getElementById('eventModalContent');
  
          modalTitle.textContent = event.title;
          modalContent.innerHTML = `
              コンテナ番号: ${event.extendedProps.container_number}<br>
              部署: ${event.extendedProps.department}<br>
              納入倉庫: ${event.extendedProps.warehouse}<br>
              入港日: ${event.extendedProps.arrival_date}<br>
              希望納品日: ${event.extendedProps.desired_delivery_date}<br>
              最適納品日: ${event.extendedProps.optimal_delivery_date}
          `;
  
          modal.style.display = 'block';
  
          var closeButton = document.querySelector('.close');
          closeButton.onclick = function() {
              modal.style.display = 'none';
          };
  
          window.onclick = function(event) {
              if (event.target == modal) {
                  modal.style.display = 'none';
              }
          };
      }
  });

  // FullCalendarの初期化
  calendar.render();
});
