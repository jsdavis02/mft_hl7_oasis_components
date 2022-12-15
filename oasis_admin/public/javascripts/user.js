$(document).ready(function () {
  let e = $("#div_endpoints");
  let r = $("#role")
  f(r, e);
  //alert('running mft_schedule.js script');
  r.on('change', function () {
    f(r, e);
  });
  $("#endpoints").multiSelect({ 
    keepOrder: true,
    cssClass: "input-group-lg mb-5",
    selectableOptgroup: true
  });
});

function f(r, e) {
  if (r.val() === 'analyst'){
    e.show();
  }
  else{
    e.hide()
  }
}