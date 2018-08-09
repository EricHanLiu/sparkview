$(document).ready(function () {
    let csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

    toastr.options = {
        "closeButton": false,
        "debug": false,
        "newestOnTop": false,
        "progressBar": false,
        "positionClass": "toast-bottom-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    $("#trends_table").DataTable({
        bFilter: false,
        bPaginate: false,
        bInfo: false,
    });

    $("#qs_table").DataTable({
        bFilter: true,
        bPaginate: true,
        pageLength: 5,
        bInfo: false,
    });

    $('#accounts').DataTable({
        'pagingType': 'full_numbers'
    });

    $("#labels").DataTable({
        'pagingType': 'full_numbers',
        'pageLength': 5
    });

    $("#adwords_datatable").DataTable({
        'pagingType': "full_numbers"
        // 'scrollY': '75%',
        // 'sScrollX': '100%',
        // 'sScrollXInner': '220%'
    });

    $("#campaign_groupings").DataTable({
        'pagingType': "full_numbers"
        // 'scrollY': '75%',
        // 'sScrollX': '100%',
        // 'sScrollXInner': '220%'
    });

    $("#clients_last_month").DataTable({
        'pagingType': "full_numbers"
        // 'scrollY': '75%',
        // 'sScrollX': '100%',
        // 'sScrollXInner': '220%'
    });

    let table = $("#clients_datatable").DataTable({
        'columnDefs': [{
            'targets': 0,
            'searchable': false,
            'orderable': false
        }],
        'order': [[1, 'asc']]
    });

    // Delete one or multiple clients
    let form = $('#delete_clients');

    form.click(function (e) {

        e.preventDefault();

        let data = table.$('input[type="checkbox"]').serialize();

        if (data) {
            $.ajax({
                url: '/budget/clients/delete/',
                headers: {'X-CSRFToken': csrftoken},
                type: 'POST',
                data: data,
                success: function (data) {
                    toastr.success("Client(s) deleted from the database.");
                    let lst = data['deleted'];
                    lst.forEach(item => {
                        let elem = $('#row-' + item['id']);
                        elem.remove();
                    })

                },
                error: function (ajaxContext) {
                    toastr.error(ajaxContext.statusText)
                },
                complete: function () {
                }

            });
        } else {
            toastr.error('Please select at least one client to delete.');

        }
    });

    let dp1 = $("#m_datepicker_1");
    let dp2 = $("#m_datepicker_2");
    let dp3 = $("#m_datepicker_3");
    let dp4 = $("#m_datepicker_4");

    dp1.on('show.bs.modal', function (event) {
        x.stopPropagation();
    });

    dp2.on('show.bs.modal', function (event) {
        event.stopPropagation();
    });

    dp3.on('show.bs.modal', function (event) {
        event.stopPropagation();
    });

    dp4.on('show.bs.modal', function (event) {
        event.stopPropagation();
    });

    // Get data from page an send it to modal
    // Userpage
    $('#m_modal_accounts').on('show.bs.modal', function (e) {

        //get data-id attribute of the clicked element
        let user_id = $(e.relatedTarget).data('userid');
        $(".modal-body #uid").val(user_id);
    });

    $('#m_modal_delete_user').on('show.bs.modal', function (e) {

        //get data-userid and data-username attribute of the clicked element
        let user_id = $(e.relatedTarget).data('userid');
        let username = $(e.relatedTarget).data('username');
        $(".modal-body #d_uid").val(user_id);
        $(".modal-header #m_title_username").html(username);
    });

    // Budget edit on view_client
    $('#m_edit_budget').on('show.bs.modal', function (e) {
        let aid = $(e.relatedTarget).data('accountid');
        let budget = $(e.relatedTarget).data('budget');
        let channel = $(e.relatedTarget).data('channel');
        $(".modal-body #aid").val(aid);
        $(".modal-body #channel").val(channel);
        $(e.currentTarget).find('input[name="budget"]').val(budget);
    });

    // Client name edit on view_client
    $('#m_edit_cname').on('show.bs.modal', function (e) {
        let c_name = $(e.relatedTarget).data('cname');
        let cid = $(e.relatedTarget).data('clientid');
        $(e.currentTarget).find('input[name="client_name"]').val(c_name);
        $(".modal-body #cid").val(cid);
    });

    $("#m_add_kpi").on('show.bs.modal', function (e) {
        let acc_id = $(e.relatedTarget).data('acc_id');
        let acc_name = $(e.relatedTarget).data('acc_name');
        $(".modal-body #acc_id").val(acc_id);
        $(".modal-body #akpi_acc_name").html(acc_name);
    });

    $("#m_add_flight_dates").on('show.bs.modal', function (e) {

        let acc_id = $(e.relatedTarget).data('acc_id');
        let acc_name = $(e.relatedTarget).data('acc_name');
        let channel = $(e.relatedTarget).data('channel');

        $(".modal-body #fd_acc_name").html(acc_name);
        $(".modal-body #fd_acc_id").val(acc_id);
        $(".modal-body #fd_acc_channel").val(channel);
    });

    $("#m_add_campaign_group").on('show.bs.modal', function (e) {

        let acc_id = $(e.relatedTarget).data('acc_id');
        let acc_name = $(e.relatedTarget).data('acc_name');
        let channel = $(e.relatedTarget).data('channel');

        $(".modal-body #cgr_acc_name").html(acc_name);
        $(".modal-body #cgr_acc_id").val(acc_id);
        $(".modal-body #cgr_channel").val(channel);
    });

    $("#m_edit_campaign_group").on('show.bs.modal', function (e) {

        let gr_id = $(e.relatedTarget).data('grid');
        let acc_name = $(e.relatedTarget).data('acc_name');
        let group_name = $(e.relatedTarget).data('group_name');
        let group_by = $(e.relatedTarget).data('group_by');
        let budget = $(e.relatedTarget).data('group_budget');
        let acc_id = $(e.relatedTarget).data('acc_id');
        let channel = $(e.relatedTarget).data('channel');

        $(e.currentTarget).find('input[name="group_budget"]').val(budget);
        $(e.currentTarget).find('input[name="cgr_group_name"]').val(group_name);
        $(e.currentTarget).find('input[name="cgr_channel"]').val(channel);

        data = {
            'account_id': acc_id,
            'gr_id': gr_id,
            'channel': channel
        };

        if (group_by === 'manual') {

            $("#gr_manual_edit").prop("checked", true);
            $($('#campaigns_gr_edit').data('select2').$container).removeClass('hidden');
            $("#cgr_group_by_edit").addClass('hidden');

            $("#campaigns_gr_edit").val(null).trigger('change');

            $.ajax({
                url: '/budget/groupings/get_campaigns/',
                headers: {'X-CSRFToken': csrftoken},
                type: 'POST',
                data: data,
                success: function (data) {
                    let campaigns = data['campaigns'];
                    let cmps_in_gr = data['group'];

                    campaigns.forEach(item => {
                        if (cmps_in_gr[0]['fields']['aw_campaigns'].length > 0) {
                            if (cmps_in_gr[0]['fields']['aw_campaigns'].includes(item['pk'])) {
                                let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], true, true);
                                $("#campaigns_gr_edit").append(new_option).trigger('change');
                            } else {
                                let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], false, false);
                                $("#campaigns_gr_edit").append(new_option).trigger('change');
                            }
                        } else if (data['group'][0]['fields']['bing_campaigns'].length > 0) {
                            if (cmps_in_gr[0]['fields']['bing_campaigns'].includes(item['pk'])) {
                                let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], true, true);
                                $("#campaigns_gr_edit").append(new_option).trigger('change');
                            } else {
                                let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], false, false);
                                $("#campaigns_gr_edit").append(new_option).trigger('change');
                            }
                        } else if (data['group'][0]['fields']['fb_campaigns'].length > 0) {
                            if (cmps_in_gr[0]['fields']['fb_campaigns'].includes(item['pk'])) {
                                let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], true, true);
                                $("#campaigns_gr_edit").append(new_option).trigger('change');
                            } else {
                                let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], false, false);
                                $("#campaigns_gr_edit").append(new_option).trigger('change');
                            }
                        } else {
                            let new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], false, false);
                            $("#campaigns_gr_edit").append(new_option).trigger('change');
                        }
                    });
                },
                error: function (ajaxContext) {
                    toastr.error(ajaxContext.statusText)
                },
                complete: function () {
                }

            });

        } else {
            $("#gr_text_edit").prop("checked", true);
            $(e.currentTarget).find('input[name="cgr_group_by_edit"]').val(group_by);
            $($('#campaigns_gr_edit').data('select2').$container).addClass('hidden');
            $("#cgr_group_by_edit").removeClass('hidden');
        }


        $(".modal-body #cgr_acc_name").html(acc_name);
        $(".modal-body #cgr_gr_id").val(gr_id);
        $(".modal-body #cgr_group_name").html(group_name);

    });

    $("#m_edit_flight_date").on('show.bs.modal', function (e) {

        let budget_id = $(e.relatedTarget).data('budgetid');
        let acc_name = $(e.relatedTarget).data('acc_name');
        let channel = $(e.relatedTarget).data('channel');
        let sdate = $(e.relatedTarget).data('sdate');
        let edate = $(e.relatedTarget).data('edate');
        let budget = $(e.relatedTarget).data('budget');

        dp3.datepicker("setDate", new Date(sdate));
        dp4.datepicker("setDate", new Date(edate));

        $(".modal-body #fde_acc_name").html(acc_name);
        $(".modal-body #fde_budget_id").val(budget_id);
        $(".modal-body #fde_acc_channel").val(channel);
        $(e.currentTarget).find('input[name="fbudget_edit"]').val(budget);
    });

    $("#m_delete_kpi").on('show.bs.modal', function (e) {
        let budgetid = $(e.relatedTarget).data('budgetid');
        let network = $(e.relatedTarget).data('network');
        $(".modal-body #bid").val(budgetid);
        $(".modal-body #dkpi_network_type").html(network);
    });

    $("#m_delete_flight_date").on('show.bs.modal', function (e) {
        let fbudgetid = $(e.relatedTarget).data('fbudgetid');
        $(".modal-body #fid").val(fbudgetid);
    });

    $("#m_delete_campaign_group").on('show.bs.modal', function (e) {
        let gr_id = $(e.relatedTarget).data('grid');
        $(".modal-body #gr_id").val(gr_id);
    });

    // Global target spend edit
    $('#m_target_spend').on('show.bs.modal', function (e) {
        let cid = $(e.relatedTarget).data('clientid');
        let target_spend = $(e.relatedTarget).data('target_spend');
        let channel = $(e.relatedTarget).data('channel');
        $(".modal-body #cid").val(cid);
        $(".modal-body #channel").val(channel);
        $(e.currentTarget).find('input[name="target_spend"]').val(target_spend);
    });

    // Handles the switch between Global Target Spend and normal client budget
    let budget_cbox = $('#m_client_budget_cbox');
    let gts_cbox = $('#m_gts_client_cbox');

    function sendAjaxRequest(d) {

        $.ajax({
            url: '/budget/gtsorbudget/',
            headers: {'X-CSRFToken': csrftoken},
            type: 'POST',
            data: d,

            success: function (data) {
                if (data['gtson'] === '1') {
                    toastr.success("Activated Global Target Spend on  " + data['client_name'] + ".");
                }
                else if (data['gtsoff'] === '1') {
                    toastr.success("Deactivated Global Target Spend on  " + data['client_name'] + ".");
                }
                else if (data['budgeton'] === '1') {
                    toastr.success("Activated Budget on  " + data['client_name'] + ".");
                }
                else if (data['budgetoff'] === '1') {
                    toastr.success("Deactivated Budget on  " + data['client_name'] + ".");
                }
            },
            error: function (ajaxContext) {
                toastr.error(ajaxContext.statusText)
            },
            complete: function () {
                setTimeout(function () {
                    location.reload()
                }, 2000)
            }
        });
    }

    budget_cbox.on('change', function () {

        let clientid = $(this).data('cid');

        if (this.checked) {
            let data = {
                budget: 'on',
                cid: clientid
            };
            sendAjaxRequest(data);
        }

        if (!this.checked) {
            let data = {
                budget: 'off',
                cid: clientid
            };
            sendAjaxRequest(data);
        }
    });

    gts_cbox.on('change', function () {

        let clientid = $(this).data('cid');

        if (this.checked) {
            let data = {
                gts: 'on',
                cid: clientid
            };
            sendAjaxRequest(data);
        }

        if (!this.checked) {
            let data = {
                gts: 'off',
                cid: clientid
            };
            sendAjaxRequest(data);
        }
    });

    $("#select_adwords").select2({
        placeholder: "Search accounts..."
    });

    $("#select_labels").select2({
        placeholder: "Search labels..."
    });

    $("#campaigns_gr").select2({
        placeholder: "Select campaigns..."
    });

    $("#campaigns_gr_edit").select2({
        placeholder: "Select campaigns..."
    });

    $($('#campaigns_gr').data('select2').$container).addClass('hidden');

    $("#gr_text").change(function () {
        $($('#campaigns_gr').data('select2').$container).addClass('hidden');
        $("#campaign_list").append('<input type="text" class="form-control group-by"\n' +
            'name="cgr_group_by" id="cgr_group_by" placeholder="Group by.." required>');
    });
    $("#gr_manual").change(function () {
        $("#cgr_group_by").remove();
        $($('#campaigns_gr').data('select2').$container).removeClass('hidden');

        data = {
            'account_id': $("#cgr_acc_id").val(),
            'channel': $("#cgr_channel").val()
        };

        $.ajax({
            url: '/budget/groupings/get_campaigns/',
            headers: {'X-CSRFToken': csrftoken},
            type: 'POST',
            data: data,
            success: function (data) {

                let campaigns = data['campaigns'];
                campaigns.forEach(item => {
                    var new_option = new Option(item['fields']['campaign_name'], item['fields']['campaign_id'], false, false);
                    $("#campaigns_gr").append(new_option).trigger('change');
                });
            },
            error: function (ajaxContext) {
                toastr.error(ajaxContext.statusText)
            },
            complete: function () {
            }

        });
    });

    $(function () {
        $("[id$='circle']").percircle();

        $("#clock").percircle({
            perclock: true
        });

        $("#countdown").percircle({
            perdown: true,
            secs: 14,
            timeUpText: 'finally!',
            reset: true
        });

        $("#custom").percircle({
            text: "custom",
            percent: 27
        });
        $("#custom-color").percircle({
            progressBarColor: "#CC3366",
            percent: 64.5
        });
    });


    $("#redBecomesBlue").percircle({percent: 61, text: "61"});
    $("#fiftyTo30").percircle({percent: 51, text: "51"});

    $('#changeCircle').click(function (e) {
        e.preventDefault();
        changeCircle();
    });
    $('#fiftyToThirtyBtn').click(function (e) {
        e.preventDefault();
        fiftyToThirty();
    });

    function changeCircle() {
        $("#redBecomesBlue").percircle({
            text: "95.5",
            percent: 95.5,
            progressBarColor: "#4f18c0"
        });
    }

    function fiftyToThirty() {
        $("#fiftyTo30").percircle({
            text: "30",
            percent: 30,
            progressBarColor: "#1ec0b0"
        });
    }


});
