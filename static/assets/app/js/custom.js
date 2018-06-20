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

    $('#accounts').DataTable({
        'pagingType': 'full_numbers'
    });

    $("#labels").DataTable({
        'pagingType': 'full_numbers'
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
        console.log(username);
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
                console.log(data);
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
});
