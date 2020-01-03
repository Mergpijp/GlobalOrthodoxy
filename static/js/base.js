$(function() {
  // Activate Select2
  $('select:not(:hidden)').select2();

  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    $('select:not(.select2-hidden-accessible,:hidden)').select2();
});  
});