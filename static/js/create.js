
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
  $('.special_select2').css("width", '100%');
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
    var data = {
        csrfmiddlewaretoken: getCookie('csrftoken'),
        input: $("#id_search_files").val(),
    }
    $.post(FILES, data, function(data, status){
        if(status === 'success') {
            $("#candidates-div").html(data["table"]);
        }
    });
}
function update_search_authors(){
    var data = {
        csrfmiddlewaretoken: getCookie('csrftoken'),
        input: $("#id_search_authors").val(),
    }
    $.post(AUTHORS, data, function(data, status){
        if(status === 'success') {
            $("#authors-candidates-div").html(data["table"]);
        }
    });
}
function update_search_translators(){
    var data = {
        csrfmiddlewaretoken: getCookie('csrftoken'),
        input: $("#id_search_translators").val(),
    }
    $.post(TRANSLATORS, data, function(data, status){
        if(status === 'success') {
            $("#translators-candidates-div").html(data["table"]);
        }
    });
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$(document).ready(function(){
    $('#id_title').on('input',function(){
        if ($("#id_title").val().length > 4) {
            update();
        }
    });
    $('#id_search_files').on('input',function(){
        if ($("#id_search_files").val().length > 0) {
            update_search_files();
        }
    });
    $('#id_search_authors').on('input',function(){
        if ($("#id_search_authors").val().length > 0) {
            update_search_authors();
        }
    });
    $('#id_search_translators').on('input',function(){
        if ($("#id_search_translators").val().length > 0) {
            update_search_translators();
        }
    });
});

