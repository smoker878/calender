document.addEventListener('DOMContentLoaded', function () {
            $('.nav-phone').hide();

        $('.nav_button').click(function () {
            // console.log("show")
            $('.nav-phone').slideToggle();
        });


    const calendarEl = document.getElementById('calendar')

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        // events: '/events',
        eventSources: [
            {
                url: '/events',
                method: 'GET',
                extraParams: function () {
                    return { t: new Date().getTime() }; // 避免快取
                },
                failure: function () {
                    Swal.fire("錯誤", "事件載入失敗", "error");
                }
            }
        ],
        customButtons: {
            newEventButton: {
                text: '新增事件!',
                click: function () {
                    needLogin(createEvent);
                }
            }
        },
        headerToolbar: {
            left: 'today newEventButton',
            center: 'prev title next',
            right: 'multiMonthYear,dayGridMonth'
        },


        dateClick: function (info) {
            console.log(info)
            needLogin(createEvent, info);
        },

        select: function (info) {
            needLogin(createEvent, info);
        },

        eventClick: function (info) {
            const event = info.event;
            eventDetail(event.id);  // 點事件直接呼叫 eventDetail
        }

    })

    calendar.render()
    window.calendar = calendar;
})

function needLogin(callback, arg) {
    $.ajax({
        url: "/auth/me",
        success: function (result) {
            // console.log(result)
            // console.log(arg)
            callback(result, arg);
        },
        error: function (xhr) {
            if (xhr.status === 401) {
                Swal.fire({
                    icon: "error",
                    title: "請登入",
                    footer: '<a href="/auth/login">🗝️登入</a>'
                })
            }
        }
    })
}

// 給後端傳來錯誤訊息時調用
function showError(err) {
    Swal.fire({
        icon: "error",
        title: "發生錯誤",
        text: err || "操作失敗，請稍後再試",
    });
}

function eventDetail(event_id) {
    $.get(`/events/${event_id}`, function (event) {
        Swal.fire({
            title: event.title,
            html: `
                <p style="white-space: pre-line;">內容:<br> ${event.content || ""}</p>
                <p>日期: ${event.start}</p>
                <p>結束: ${event.end || "無"}</p>
                <p>公開: ${event.is_public ? "是" : "否"}</p>
               <!-- <p>群組: ${event.group_id || "無"}</p> -->
                <p>創建: ${event.username || "無"}</p>
            `,
            // showCancelButton: true,
            showDenyButton: true, 
            confirmButtonText: "修改",
            // cancelButtonText: "刪除",
            denyButtonText: "刪除"
        }).then((result) => {
            // console.log(result)
            // console.log(event)
            if (result.isConfirmed) {
                needLogin(editEvent, event.id);
            // } else if (result.dismiss === Swal.DismissReason.cancel) {
            } else if (result.isDenied) {
                needLogin(deleteEvent, event.id);
            }
        });
    }).fail(function (xhr) {
        showError(xhr.responseJSON?.error || "取得事件資料失敗");
    });
}

function createEvent(auth = {}, info = {}) {
    Swal.fire({
        title: "新增事件",
        html: `
            <label> 標題</label><input id="title" class="swal2-input" placeholder="標題"><br>
            <label> 內容</label><textarea id="content" class="swal2-textarea" placeholder="內容"></textarea><br>
            <label> 日期</label><input id="start" type="date" class="swal2-input" value="${info.startStr || info.dateStr}"><br>
            <label> 結束(多日)</label><input id="end" type="date" class="swal2-input" value="${info.endStr || ""}"><br>
            <label> <input type="checkbox" id="is_public">公開事件</label>
        `,
        showCancelButton: true,
        confirmButtonText: "送出"
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/events",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    title: $("#title").val(),
                    content: $("#content").val(),
                    start: $("#start").val(),
                    end: $("#end").val(),
                    is_public: $("#is_public").is(":checked")
                }),
                success: function () {
                    Swal.fire("成功", "事件已新增", "success");

                    console.log("Will call refetchEvents()", calendar);
                    calendar.refetchEvents();
                    // calendar.refetchEvents();
                },
                error: function (xhr) {
                    showError(xhr.responseJSON.error || "新增失敗");
                }
            });
        }
    });
}

function editEvent(_, event_id) {
    // console.log(event_id)

    $.get(`/events/${event_id}`, function (event) {
        Swal.fire({
            title: "編輯事件",
            html: `
                <label> 標題</label><input id="title" class="swal2-input" value="${event.title}"><br>
                <label> 內容</label><textarea id="content" class="swal2-textarea">${event.content || ""}</textarea><br>
                <label> 日期</label><input id="start" type="date" class="swal2-input" value="${event.start}"><br>
                <label> 結束</label><input id="end" type="date" class="swal2-input" value="${event.end || ""}"><br>
                <label><input type="checkbox" id="is_public" ${event.is_public ? "checked" : ""}> 公開事件</label>
            `,
            showCancelButton: true,
            confirmButtonText: "更新"
        }).then((result) => {
            console.log(result)

            if (result.isConfirmed) {
                $.ajax({
                    url: `/events/${event_id}`,
                    method: "PUT",
                    contentType: "application/json",
                    data: JSON.stringify({
                        title: $("#title").val(),
                        content: $("#content").val(),
                        start: $("#start").val(),
                        end: $("#end").val(),
                        is_public: $("#is_public").is(":checked")
                    }),
                    success: function () {
                        Swal.fire("成功", "事件已更新", "success");
                        calendar.refetchEvents();
                    },
                    error: function (xhr) {
                        showError(xhr.responseJSON.error || "更新失敗");
                    }
                });
            }
        });
    });
}

function deleteEvent(_, event_id) {
    Swal.fire({
        title: "確定要刪除嗎？",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "刪除"
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/events/${event_id}`,
                method: "DELETE",
                success: function () {
                    Swal.fire("刪除成功", "", "success");
                    calendar.refetchEvents();
                },
                error: function (xhr) {
                    showError(xhr.responseJSON.error || "刪除失敗");
                }
            });
        }
    });
}







