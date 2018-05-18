$(document).ready(function () {
    tbl = $('#accounts').DataTable({
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

    var table = $("#clients_datatable").DataTable({
        'columnDefs': [{
            'targets': 0,
            'searchable': false,
            'orderable': false
            // 'render': function (data, type, full, meta) {
            //     return '<input type="checkbox" name="id-{{ client_data.client_id }}" value="' + $('<div/>').text(data).html() + '">';

        }],
        'order': [[1, 'asc']]
    });

    $('#clients_select_all').on('click', function () {
        // Get all rows with search applied
        var rows = table.rows({'search': 'applied'}).nodes();
        // Check/uncheck checkboxes for all rows in the table
        $('input[type="checkbox"]', rows).prop('checked', this.checked);
    });

    $('#clients_datatable tbody').on('change', 'input[type="checkbox"]', function () {
        // If checkbox is not checked
        if (!this.checked) {
            var el = $('#clients_select_all').get(0);
            // If "Select all" control is checked and has 'indeterminate' property
            if (el && el.checked && ('indeterminate' in el)) {
                // Set visual state of "Select all" control
                // as 'indeterminate'
                el.indeterminate = true;
            }
        }
    });

    var form = $('#delete_clients');
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    form.click(function (e) {

        e.preventDefault();

        var data = table.$('input[type="checkbox"]').serialize();

        if (data) {
            $.ajax({
                url: '/budget/clients/delete/',
                headers: {'X-CSRFToken': csrftoken},
                type: 'POST',
                data: data,
                success: function () {
                    swal({
                        "title": "SUCCESS",
                        "text": "Client(s) deleted from the database.",
                        "type": "success",
                        "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                    });
                },
                error: function (ajaxContext) {
                    swal({
                        "title": "ERROR",
                        "text": ajaxContext.statusText,
                        "type": "error",
                        "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                    });
                },
                complete: function () {
                    setTimeout(function () {
                        location.reload();
                    }, 2500);
                }

            });
        } else {
            swal({
                'title': 'ERROR',
                'text': 'Please select at least one client to delete.',
                'type': 'error',
                'confirmButtonClass': 'btn btn-secondary m-btn m-btn--wide'
            });
        }

    });
    $('#m_modal_accounts').on('show.bs.modal', function (e) {

        //get data-id attribute of the clicked element
        var user_id = $(e.relatedTarget).data('userid');
        $(".modal-body #uid").val(user_id);
    });

    $('#m_edit_budget').on('show.bs.modal', function(e){
        var aid = $(e.relatedTarget).data('accountid');
        var budget = $(e.relatedTarget).data('budget');
        var channel = $(e.relatedTarget).data('channel');
        $(".modal-body #aid").val(aid);
        $(".modal-body #channel").val(channel);
        $(e.currentTarget).find('input[name="budget"]').val(budget);
    });

        $('#m_target_spend').on('show.bs.modal', function(e){
        var cid = $(e.relatedTarget).data('clientid');
        var target_spend = $(e.relatedTarget).data('target_spend');
        var channel = $(e.relatedTarget).data('channel');
        $(".modal-body #cid").val(cid);
        $(".modal-body #channel").val(channel);
        $(e.currentTarget).find('input[name="target_spend"]').val(target_spend);
    });
})
;
