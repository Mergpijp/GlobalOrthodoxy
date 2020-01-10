$(function() {
  // Activate Select2
  $('select:not(:hidden)').select2();

  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    $('select:not(.select2-hidden-accessible,:hidden)').select2();
});  
$('button').click(function(){
   $('#id_title_original').toggleClass(function(){
      return $(this).is('.rtl-direction, .ltr-direction') ? 'rtl-direction ltr-direction' : 'rtl-direction';
  })
})
});
