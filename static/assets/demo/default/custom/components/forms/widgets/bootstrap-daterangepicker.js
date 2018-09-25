const csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
const account_id = jQuery("[name=account_id]").val();

function getAnomaliesData(data) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'sapi/',
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
        // console.log("Creating interval");
        let intervalId = setInterval(() => {
            $.ajax({
                url: 'sapi/',
                headers: {'X-CSRFToken': csrftoken},
                type: 'GET',
                data: {task_id: task_id},
                success: (res) => {
                    // console.log("Requested task state");
                    // console.log(res);
                    if (res['tstate'] === 'SUCCESS') {
                        // console.log(res);
                        // console.log("Task Done");
                        resolve({intervalId: intervalId, data: res})
                    }
                },
                complete: (data) => {
                }
            })
        }, 2000);
    })
}

var BootstrapDaterangepicker = {
    init: function () {
        !function () {
            var a = moment().subtract(29, "days")
                , t = moment();
            $("#m_daterangepicker_6").daterangepicker({
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
                // On selecting the second daterange we initiate the ajax call to fetch data
                $("#m_daterangepicker_7").on('apply.daterangepicker', function (ev, picker) {

                    let first_minDate = $("#m_daterangepicker_6").data('daterangepicker').startDate.format('YYYY-MM-DD');
                    let first_maxDate = $("#m_daterangepicker_6").data('daterangepicker').endDate.format('YYYY-MM-DD');

                    let second_minDate = picker.startDate.format('YYYY-MM-DD');
                    let second_maxDate = picker.endDate.format('YYYY-MM-DD');

                    let table = $("#adwords_anomalies_datatable");
                    let table_wrapper = $('#anomalies_wrapper');


                    data = {
                        'account_id': account_id,
                        'fmin': first_minDate,
                        'fmax': first_maxDate,
                        'smin': second_minDate,
                        'smax': second_maxDate
                    };
                    // Block table
                    mApp.block("#m-content-block", {
                        overlayColor: "#000000",
                        type: "loader",
                        state: "primary",
                        size: "lg"
                    });


                    // console.log("Making initial request");
                    getAnomaliesData(data).then(res => {
                        // console.log("Task send and retrieved id");
                        // console.log(res);
                        setTasker(res['tid']).then(res2 => {
                            // console.log("Results are: ");
                            // console.log(JSON.parse(res2.data.tresult));
                            clearInterval(res2.intervalId);
                            // Populate Datatable

                            if ($.fn.DataTable.fnIsDataTable(table)) {
                                table.DataTable().clear();
                                table.DataTable().destroy();
                                table.remove();
                                table_wrapper.append('<table class="table table-striped m-table" id="adwords_anomalies_datatable">' +
                                    '<thead>' +
                                    '<tr>' +
                                    '<th>Impr. Share</th>' +
                                    '<th>Impressions</th>' +
                                    '<th>Clicks</th>' +
                                    '<th>CTR</th>' +
                                    '<th>Avg. CPC</th>' +
                                    '<th>Cost</th>' +
                                    '<th>Conversions</th>' +
                                    '<th>Cost / Conv.</th>' +
                                    '</tr>' +
                                    '</thead>' +
                                    '<tbody></tbody>' +
                                    '</table>');
                                // console.log('DT');

                                let e = JSON.parse(res2.data.tresult);

                                let result = [];
                                let arr = [];

                                Object.keys(e).forEach(function (key) {
                                    result[key.replace(/[./]/g, '')] = e[key];
                                });

                                arr.push(result);

                                $("#adwords_anomalies_datatable").DataTable({
                                    bDestroy: true,
                                    bProcessing: false,
                                    pageLength: 25,
                                    data: arr,
                                    columns: [
                                        {
                                            'data': "search_impr_share",
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + data[1] + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + data[2] + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'impressions',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber(data[1], 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber(data[2], 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'clicks',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber(data[1], 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber(data[2], 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'ctr',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + data[1] + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + data[2] + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'avg_cpc',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber((data[1] / 1000000), 3) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber((data[2] / 1000000), 3) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + data[0].toFixed(2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'cost',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber((data[1] / 1000000), 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber((data[2] / 1000000), 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'conversions',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber(data[1], 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber(data[2], 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'cost__conv',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber((data[1] / 1000000), 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber((data[2] / 1000000), 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        }
                                    ],
                                    language: {
                                        sSearch: '<i class="fa fa-search"></i>',
                                    }
                                });
                            } else {
                                table_wrapper.append('<table class="table table-striped m-table" id="adwords_anomalies_datatable">' +
                                    '<thead>' +
                                    '<tr>' +
                                    '<th>Impr. Share</th>' +
                                    '<th>Impressions</th>' +
                                    '<th>Clicks</th>' +
                                    '<th>CTR</th>' +
                                    '<th>Avg. CPC</th>' +
                                    '<th>Cost</th>' +
                                    '<th>Conversions</th>' +
                                    '<th>Cost / Conv.</th>' +
                                    '</tr>' +
                                    '</thead>' +
                                    '<tbody></tbody>' +
                                    '</table>');

                                let e = JSON.parse(res2.data.tresult);

                                let result = [];
                                let arr = [];

                                Object.keys(e).forEach(function (key) {
                                    result[key.replace(/[./]/g, '')] = e[key];
                                });

                                arr.push(result);

                                $("#adwords_anomalies_datatable").DataTable({
                                    bDestroy: true,
                                    bProcessing: false,
                                    pageLength: 25,
                                    data: arr,
                                    columns: [
                                        {
                                            'data': "search_impr_share",
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + data[1] + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + data[2] + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'impressions',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber(data[1], 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber(data[2], 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'clicks',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber(data[1], 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber(data[2], 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'ctr',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + data[1] + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + data[2] + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'avg_cpc',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber((data[1] / 1000000), 3) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber((data[2] / 1000000), 3) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + data[0].toFixed(2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'cost',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber((data[1] / 1000000), 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber((data[2] / 1000000), 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'conversions',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber(data[1], 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber(data[2], 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        },
                                        {
                                            'data': 'cost__conv',
                                            "render": function (data, type, row, meta) {
                                                if (type === 'display') {
                                                    rdata = '<p style="margin-bottom: 0!important;" class="text-center"><b>' + Humanize.formatNumber((data[1] / 1000000), 2) + '</b></p>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center"><small>' + Humanize.formatNumber((data[2] / 1000000), 2) + '</small>' +
                                                        '<p style="margin-bottom: 0!important;" class="text-center">';

                                                    if (data[0] > 0) {
                                                        var badge = '<span class="m-badge m-badge--success m-badge--wide">'
                                                    } else if (data[0] === 0) {
                                                        var badge = '<span class="m-badge m-badge--metal m-badge--wide">'
                                                    } else {
                                                        var badge = '<span class="m-badge m-badge--danger m-badge--wide">'
                                                    }

                                                    rdata = rdata + badge + Humanize.formatNumber(data[0], 2) + '%</span></p>';
                                                } else if (type === 'sort') {
                                                    rdata = data[1];
                                                }
                                                return rdata;
                                            }
                                        }
                                    ],
                                    language: {
                                        sSearch: '<i class="fa fa-search"></i>',
                                    }
                                });
                                // console.log('Finished');
                            }


                            // Unblock table
                            mApp.unblock("#m-content-block")
                        })
                    })


                });
        }()
    }
};
jQuery(document).ready(function () {
    BootstrapDaterangepicker.init()
});


