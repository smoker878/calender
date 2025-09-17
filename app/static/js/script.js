document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar')

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        events: '/calendar/events',
        customButtons: {
            newEventButton: {
                text: '新增事件!',
                click: function () {
                    alert('clicked the custom button!')
                }
            }
        },
        headerToolbar: {
            left: 'today newEventButton',
            center: 'prev title next',
            right: 'multiMonthYear,dayGridMonth'
        },

        // 點選日期 -> 新增事件
        select: function (info) {

        },

        eventClick: function (info) {
            alert('事件：' + info.event.title)
        }
    })

    calendar.render()
})

function needLogin(callback, arg) {
    $.ajax({
        url: "/auth/me",
        success: function(result) {
            callback(result, arg);
        },
        error: function(xhr) {
            if (xhr.status === 401) {
                Swal.fire({
                    icon: "error",
                    title: "請登入",
                    footer: '<a href="/auth/login">🗝️登入</a>'
                });
            }
        }
    });
}








