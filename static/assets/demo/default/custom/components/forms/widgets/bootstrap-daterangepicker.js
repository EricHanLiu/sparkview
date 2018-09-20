const csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

function getAnomaliesData(data) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'test/',
            headers: {'X-CSRFToken': csrftoken},
            type: 'POST',
            data: data,
            success: function (data) {
                resolve(data);
            },
            error: function (ajaxContext) {
                toastr.error(ajaxContext.statusText)
            },
            complete: function () {
            }

        });
    })
}

function setTasker(task_id) {
    return new Promise((resolve, reject) => {
        console.log("Creating interval");
        let intervalId = setInterval(() => {
            $.ajax({
                url: 'test/',
                headers: {'X-CSRFToken': csrftoken},
                type: 'GET',
                data: {task_id: task_id},
                success: (res) => {
                    console.log("Requested task state");
                    console.log(res);
                    if (res['tstate'] === 'SUCCESS') {
                        console.log(res);
                        console.log("Task Done");
                        resolve({intervalId: intervalId, data:res})
                    }
                },
                complete: (data) => {
                }
            })
        }, 1000);
    })
}

var BootstrapDaterangepicker = {
    init: function () {
        !function () {
            var a = moment().subtract(29, "days")
                , t = moment();
            $("#m_daterangepicker_6, #m_daterangepicker_7").daterangepicker({
                buttonClasses: "m-btn btn",
                applyClass: "btn-success",
                cancelClass: "btn-danger",
                startDate: a,
                endDate: t,
                ranges: {
                    Today: [moment(), moment()],
                    Yesterday: [moment().subtract(1, "days"), moment().subtract(1, "days")],
                    "Last 7 Days": [moment().subtract(6, "days"), moment()],
                    "Last 30 Days": [moment().subtract(29, "days"), moment()],
                    "This Month": [moment().startOf("month"), moment().endOf("month")],
                    "Last Month": [moment().subtract(1, "month").startOf("month"), moment().subtract(1, "month").endOf("month")]
                }
            }, function (a, t, n) {
                $("#m_daterangepicker_6 .form-control").val(a.format("DD/MM/YYYY") + " - " + t.format("DD/MM/YYYY"))
            }),
                $("#m_daterangepicker_7").daterangepicker({
                    buttonClasses: "m-btn btn",
                    applyClass: "btn-success",
                    cancelClass: "btn-danger",
                    startDate: a,
                    endDate: t,
                    ranges: {
                        Today: [moment(), moment()],
                        Yesterday: [moment().subtract(1, "days"), moment().subtract(1, "days")],
                        "Last 7 Days": [moment().subtract(6, "days"), moment()],
                        "Last 30 Days": [moment().subtract(29, "days"), moment()],
                        "This Month": [moment().startOf("month"), moment().endOf("month")],
                        "Last Month": [moment().subtract(1, "month").startOf("month"), moment().subtract(1, "month").endOf("month")]
                    }
                }, function (a, t, n) {
                    $("#m_daterangepicker_7 .form-control").val(a.format("DD/MM/YYYY") + " - " + t.format("DD/MM/YYYY"))
                }),
                $("#m_daterangepicker_7").on('apply.daterangepicker', function (ev, picker) {

                    let first_minDate = $("#m_daterangepicker_6").data('daterangepicker').startDate.format('DD-MM-YYYY');
                    let first_maxDate = $("#m_daterangepicker_6").data('daterangepicker').endDate.format('DD-MM-YYYY');

                    let second_minDate = picker.startDate.format('YYYY-MM-DD');
                    let second_maxDate = picker.endDate.format('YYYY-MM-DD');

                    data = {
                        'fmin': first_minDate,
                        'fmax': first_maxDate,
                        'smin': second_minDate,
                        'smax': second_maxDate
                    };
                    // Start BlockUI

                    console.log("Making initial request");
                    getAnomaliesData(data).then(res => {
                        console.log("Task send and retrieved id");
                        console.log(res);
                        setTasker(res['tid']).then( res2 => {
                            console.log("Results are:");
                            console.log(res2.data);
                            clearInterval(res2.intervalId);
                            // Pop
                            // END BlockUI
                        })
                    })


                });
        }()
    }
};
jQuery(document).ready(function () {
    BootstrapDaterangepicker.init()
});
