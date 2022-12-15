$(document).ready(function () {
  //alert('running mft_schedule.js script');
  $("#action").on('change', function () {
    showSelected();
  });
  $("#primary_export_item").on('change', function () {
    showExportSelected();
  });
  hideAll();
  showSelected();
  subhideAll();
  //showExportSelected();
});
function showExportSelected() {
  //alert($("#primary_export_item").val());
  subhideAll();
  
  switch ($("#primary_export_item").val()) {
    case "Endpoint":
      $("#div_endpoint_type").show();
      
      $("#div_route_type").hide();
      
      break;
    case "Route":
      $("#div_route_type").show();
      
      $("#div_endpoint_type").hide();
      break;
  }
}
function showSelected() {
  //alert('running showselected function');
  hideAll();
  subhideAll();
  switch ($("#action").val()) {
    case "Import":
      $("#div_import_file").show();
      $("#div_active").hide();
      break;
    case "Export":
      $("#div_primary_export_item").show();
      $("#div_active").show();
      showExportSelected();
      break;
    default:
      //do nothing
  }
}

function hideAll() {
  $("#div_import_file").hide();
  $("#div_primary_export_item").hide();
  $("#div_active").hide();
  subhideAll();
}

function subhideAll() {
  $("#div_route_type").hide();
  $("#div_endpoint_type").hide();
  
}