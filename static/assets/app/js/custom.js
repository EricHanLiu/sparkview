$(document).ready(function () {


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

    $("#adwords_datatable").DataTable({
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
    let csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
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

    // Budget edit on view_client
    $('#m_edit_budget').on('show.bs.modal', function (e) {
        let aid = $(e.relatedTarget).data('accountid');
        let budget = $(e.relatedTarget).data('budget');
        let channel = $(e.relatedTarget).data('channel');
        $(".modal-body #aid").val(aid);
        $(".modal-body #channel").val(channel);
        $(e.currentTarget).find('input[name="budget"]').val(budget);
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

    budget_cbox.on('change', function () {
        if (this.checked){
            console.log('Budget checked');
        }
    })

    gts_cbox.on('change', function () {
        if (this.checked){
            console.log('Global Target Spend');
        }
    })
});
