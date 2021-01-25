
function unsetInlineWidthOfSelect2($element) {
  $element.find('.select2-container').each(function (i, selectTwoContainer) {
  	// ViaCss: If you want control via CSS, set width to ''
    $(selectTwoContainer).css('width', ''); 
    // ViaEventReaction: If you want full width
    //$(selectTwoContainer).css('width', '100%'); 
  });
}
$(function() {
  // Activate Select2
  $('#tab1_select2_single').select2();
  $('#tab1_select2_multiple').select2();
  $('#tab2_select2_single').select2();
  $('#tab2_select2_multiple').select2();
  $('#tab3_select2_single').select2();
  $('#tab3_select2_multiple').select2();

  // Width hack
  $.fn.select2.defaults.set("width", '100%');
  $('#tab4_select2_single').select2();
  $('#tab4_select2_multiple').select2();

  $('#tab5_select2_single').select2();
  $('#tab5_select2_multiple').select2();

  // Everything is loaded, hide the tab2
  $('#tab3').removeClass('active');
});
unsetInlineWidthOfSelect2($(document));

function update(){
    var data = {'input': $("#id_title").val()};
    $.get(URL, data, function(data, status){
        if(status === 'success') {
            $('#language_title').html(data);
        }
    });
}
function update_search_files(){
    var data = {'input': $("#id_search_files").val()};
    $.get(FILES, data, function(data, status){
        if(status === 'success') {
            $('#id_search_files').html(data);
        }
    });
}
$(document).ready(function(){
    $('#id_title').on('input',function(){
        if ($("#id_titlel").val().length > 4) {
            update();
        }
    });
    $('#id_search_files').on('input',function(){
        if ($("#id_search_files").val().length > 0) {
            update_search_files();
        }
    });
    $('select').selectize({
          sortField: 'text'
    });
});
