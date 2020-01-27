$.fn.select2.defaults.set( "theme", "bootstrap4" );
$(document).on('click', '.confirm-delete', function(){
    return confirm('Are you sure you want to delete this?');
})