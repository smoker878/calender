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
        // 處理圖片
        let imageHtml = "";
        if (event.images && event.images.length > 0) {
            // 檢查是字串還是物件
            imageHtml = event.images
                .map(img => {
                    const filename = `${img.filename}`; // 假設你的圖片存在 /uploads/
                    return `
                        <div class="preview-item">
                            <img src="uploads/${filename}" class="preview-thumb" alt="event image">
                        </div>`;
                })
                .join("");
        }

        Swal.fire({
            title: event.title,
            html: `
                <p style="white-space: pre-line;">內容:<br> ${event.content || ""}</p>
                <p>日期: ${event.start}</p>
                <p>結束: ${event.end || "無"}</p>
                <p>公開: ${event.is_public ? "是" : "否"}</p>
                <p>創建: ${event.username || "無"}</p>
                <div id="previewContainer" class="preview-container">
                    ${imageHtml}
                </div>
            `,
            showDenyButton: true,
            confirmButtonText: "修改",
            denyButtonText: "刪除",
            didOpen: () => {
                initDropzone("#my-dropzone", uploadedImages, "#previewContainer");
            }
        }).then((result) => {
            if (result.isConfirmed) {
                needLogin(editEvent, event.id);
            } else if (result.isDenied) {
                needLogin(deleteEvent, event.id);
            }
        });
    }).fail(function (xhr) {
        showError(xhr.responseJSON?.error || "取得事件資料失敗");
    });
}

let uploadedImages = []; // 用來收集後端回傳的檔名
function createEvent(auth = {}, info = {}) {
    uploadedImages.length = 0;
    Swal.fire({
        title: "新增事件",
        html: `
            <label> 標題</label><input id="title" class="swal2-input" placeholder="標題"><br>
            <label> 內容</label><textarea id="content" class="swal2-textarea" placeholder="內容"></textarea><br>
            <label> 日期</label><input id="start" type="date" class="swal2-input" value="${info.startStr || info.dateStr}"><br>
            <label> 結束(多日)</label><input id="end" type="date" class="swal2-input" value="${info.endStr || ""}"><br>
            <label><input type="checkbox" id="is_public">公開事件</label><br><br>

            <!-- Dropzone -->
            <form action="/upload" class="dropzone" id="my-dropzone"></form>
            <div id="previewContainer" class="preview-container"></div>
        `,
        showCancelButton: true,
        confirmButtonText: "送出",
        didOpen: () => {
            initDropzone("#my-dropzone", uploadedImages, "#previewContainer");
        }
    }).then((result) => {
        if (result.isConfirmed) {
            console.log(uploadedImages)
            $.ajax({
                url: "/events",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    title: $("#title").val(),
                    content: $("#content").val(),
                    start: $("#start").val(),
                    end: $("#end").val(),
                    is_public: $("#is_public").is(":checked"),
                    images: uploadedImages.map(filename => ({ filename })),
                }),
                success: function () {
                    Swal.fire("成功", "事件已新增", "success");
                    calendar.refetchEvents();
                },
                error: function (xhr) {
                    showError(xhr.responseJSON.error || "新增失敗");
                }
            });
        }
    });
}


// ---------------
function editEvent(_, event_id) {
    let uploadedImages = []; // 重新宣告

    $.get(`/events/${event_id}`, function (event) {
        let imageHtml = "";

        if (event.images && event.images.length > 0) {
            imageHtml = event.images.map(img => {
                uploadedImages.push(img.filename);
                return `
                    <div class="preview-item">
                        <img src="uploads/${img.filename}" class="preview-thumb" alt="event image">
                        <button class="remove-btn" data-filename="${img.filename}">✖</button>
                    </div>
                `;
            }).join("");
        }

        Swal.fire({
            title: "編輯事件",
            html: `
                <label> 標題</label><input id="title" class="swal2-input" value="${event.title}"><br>
                <label> 內容</label><textarea id="content" class="swal2-textarea">${event.content || ""}</textarea><br>
                <label> 日期</label><input id="start" type="date" class="swal2-input" value="${event.start}"><br>
                <label> 結束</label><input id="end" type="date" class="swal2-input" value="${event.end || ""}"><br>
                <label><input type="checkbox" id="is_public" ${event.is_public ? "checked" : ""}> 公開事件</label><br><br>

                <!-- Dropzone -->
                <form action="/upload" class="dropzone" id="my-dropzone"></form>
                <div id="previewContainer" class="preview-container">${imageHtml}</div>
            `,
            showCancelButton: true,
            confirmButtonText: "更新",
            didOpen: () => {
                // 初始化 Dropzone
                initDropzone("#my-dropzone", uploadedImages, "#previewContainer");

                // 綁定刪除事件
                $("#previewContainer").on("click", ".remove-btn", function () {
                    const filename = $(this).data("filename");
                    $(this).closest(".preview-item").remove();
                    uploadedImages = uploadedImages.filter(name => name !== filename);
                });
            }
        }).then((result) => {
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
                        is_public: $("#is_public").is(":checked"),
                        images: uploadedImages.map(filename => ({ filename })),  // ✅ 加入圖片
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


// 上傳圖片
function initDropzone(selector, uploadedImages, previewContainerSelector) {
    const myDropzone = new Dropzone(selector, {
        url: "/upload",
        maxFilesize: 5,
        acceptedFiles: "image/*",
        addRemoveLinks: false,
        dictDefaultMessage: "拖曳圖片到這裡或點擊上傳",
    });

    myDropzone.on("success", function (file, response) {
        const uuidName = response.filename; // 後端回傳
        uploadedImages.push(uuidName); // 加到傳入的 array
        console.log(uploadedImages)

        // 若要預覽圖片
        const reader = new FileReader();
        reader.onload = function (e) {
            const preview = $(`
                <div class="preview-item">
                    <img src="${e.target.result}" class="preview-thumb">
                    <button class="remove-btn">✖</button>
                </div>
            `);
            preview.find(".remove-btn").on("click", function () {
                preview.remove();
                preview.remove();
                const index = uploadedImages.indexOf(uuidName);
                if (index > -1) {
                    uploadedImages.splice(index, 1); // 正確修改原陣列
                }
            });
            $(previewContainerSelector).append(preview);
        };
        reader.readAsDataURL(file);
    });

    myDropzone.on("error", function (file, err) {
        console.error("上傳錯誤:", err);
    });
}






