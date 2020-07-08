
$(document).on('click', '.confirm-delete', function(){
    return confirm('Are you sure you want to delete this?');
})

$(document).on('click', '.confirm-delete-pub', function(){
    return confirm('Are you sure you want to delete this? This publication will be place in the thrashbin.');
})


$(document).on('click', '.confirm-logout', function(){
    return confirm('Are you sure you want to logout?');
})

function toggleFileUpload() {
  var x = document.getElementById("drop_zone");
  var y = document.getElementById("div_id_file")
  if (x.style.display === "none") {
    x.style.display = "block";
    y.style.display = "none";
  } else {
    x.style.display = "none";
    y.style.display = "block";
  }
}
