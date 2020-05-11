
$(document).on('click', '.confirm-delete', function(){
    return confirm('Are you sure you want to delete this?');
})

$(document).on('click', '.confirm-delete-pub', function(){
    return confirm('Are you sure you want to delete this? This publication will be place in the thrashbin.');
})


$(document).on('click', '.confirm-logout', function(){
    return confirm('Are you sure you want to logout?');
})


