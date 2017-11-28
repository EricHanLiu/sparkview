$(document).ready(function() {
  $('#accounts').DataTable({
      'pagingType': 'full_numbers',
  });

  $("#adwords_datatable").DataTable({
    'pagingType': "full_numbers",
    // 'scrollY': '75%',
    // 'sScrollX': '100%',
    // 'sScrollXInner': '220%'
  });
});
