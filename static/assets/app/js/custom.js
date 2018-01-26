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

    $('#clients_datatable tbody').on('change', 'input[type="checkbox"]', function(){
   // If checkbox is not checked
   if(!this.checked){
      var el = $('#clients_select_all').get(0);
      // If "Select all" control is checked and has 'indeterminate' property
      if(el && el.checked && ('indeterminate' in el)){
         // Set visual state of "Select all" control
         // as 'indeterminate'
         el.indeterminate = true;
      }
   }

   // var form = $('#delete_clients');
   // $('#delete_clients').on('submit', function(e){
   //    console.log(form);
   //
   //    table.$('input[type="checkbox"]').each(function(){
   //       // If checkbox doesn't exist in DOM
   //       if(!$.contains(document, this)){
   //          // If checkbox is checked
   //          if(this.checked){
   //             // Create a hidden element
   //             $(form).append(
   //                $('<input>')
   //                   .attr('type', 'hidden')
   //                   .attr('name', this.name)
   //                   .val(this.value)
   //             );
   //          }
   //       }
   //    });
   //    var data = form.serialize();
   //    console.log(data);
   //    form.ajaxSubmit({
   //        type: 'POST',
   //        headers: {'X-CSRFToken': csrftoken},
   //        data: data,
   //        url: '/budget/clients/delete/',
   //        success: function() {
   //            swal({
   //                  "title": "",
   //                  "text": "New client added to the database.",
   //                  "type": "success",
   //                  "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"},
   //                  function(){
   //                     location.reload();
   //                  });
   //            },
   //        error: function(ajaxContext) {
   //            swal({
   //                "title": "",
   //                "text": ajaxContext.statusText,
   //                "type": "error",
   //                "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
   //            });
   //        }
   //    });
   // });

    });
});
