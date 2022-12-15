$(document).ready(function () {
  $("form").submit(function (event) {
    let freq_type = $("#freq_type").val();
    let sub_day = $("#sub_day_freq_type").val();
    let spec_time = $("#spec_time").val();
    let spec_date = $("#spec_date").val();
    //if daily, weekly, monthly or yearly we must have a spec time
    let spec_time_required = 'Daily, Weekly, Monthly or Yearly that do not have a sub day schedule require a Specific Time to be set!';
    let spec_time_and_date_required = 'Specific Date and Time Fields must be filled out for this Frequency Type!';
    let spec_date_required = 'Specific Date required, for Yearly only day and month are used.';
    if(freq_type === 'Daily' || freq_type === 'Weekly' || freq_type === 'Monthly'){
      if(sub_day === 'None'){
        if(spec_time.length<=0){
          alert(spec_time_required);
          event.preventDefault();
          return false;
        }
      }
    }
    if(freq_type === 'Specific_Date_and_Time' || freq_type === 'Yearly'){
      if(sub_day === 'None'){
        if(spec_time.length<=0 || spec_date.length<=0){
          alert(spec_time_and_date_required);
          event.preventDefault();
          return false;
        }
      }
      else if(sub_day !== 'None' && freq_type === 'Yearly' && spec_date.length<=0){
        alert(spec_date_required);
        event.preventDefault();
        return false;
      }
    }
  });
  //alert('running mft_schedule.js script');
  $("#producer_type").on('change', function () {
    showSelected('producer');
  });
  $("#consumer_type").on('change', function () {
    showSelected('consumer');
  });
  $("#producer_msg_types").multiSelect({keepOrder: true});
  $("#consumer_msg_types").multiSelect({keepOrder: true});
  hideAll('producer');
  hideAll('consumer');
  $("#consumer_msg_types").multiSelect({
    keepOrder: true,
    cssClass: "input-group-lg mb-5",
    selectableOptgroup: true
  });
  
});

function showSelected(endpoint_direction) {
  //alert('running showselected function');
  hideAll(endpoint_direction);
  let ed_type_id = "#"+endpoint_direction+"_type";
  switch ($(ed_type_id).val()) {
    case "MFT-FS":
      $("#div_"+endpoint_direction+"_host").show();
      $("#div_"+endpoint_direction+"_file_path").show();
      $("#div_"+endpoint_direction+"_file_scheme").show();
      $("#div_"+endpoint_direction+"_schedule").show();
      $("#div_"+endpoint_direction+"_delete_source").show();
      break;
    case "MFT-SMB":
      $("#div_"+endpoint_direction+"_host").show();
      $("#div_"+endpoint_direction+"_file_path").show();
      $("#div_"+endpoint_direction+"_file_scheme").show();
      $("#div_"+endpoint_direction+"_schedule").show();
      $("#div_"+endpoint_direction+"_delete_source").show();
      break;
    case "MFT-SFTP-Client":
      $("#div_"+endpoint_direction+"_host").show();
      $("#div_"+endpoint_direction+"_port").show();
      $("#div_"+endpoint_direction+"_username").show();
      $("#div_"+endpoint_direction+"_pass").show();
      $("#div_"+endpoint_direction+"_file_path").show();
      $("#div_"+endpoint_direction+"_file_scheme").show();
      $("#div_"+endpoint_direction+"_schedule").show();
      $("#div_"+endpoint_direction+"_delete_source").show();
      break;
    case "HL7":
      $("#div_"+endpoint_direction+"_host").show();
      $("#div_"+endpoint_direction+"_port").show();
      $("#div_"+endpoint_direction+"_msg_types").show();
      break;
    case "unknown":
     
      break;
    
    default:
      //do nothing
  }
}

function hideAll(endpoint_direction) {
  if(endpoint_direction === 'producer'){
    $("#div_producer_host").hide();
    $("#div_producer_port").hide();
    $("#div_producer_file_path").hide();
    $("#div_producer_file_scheme").hide();
    $("#div_producer_username").hide();
    $("#div_producer_pass").hide();
    $("#div_producer_schedule").hide();
    $("#div_producer_msg_types").hide();
    $("#div_producer_delete_source").hide();
  }
  if(endpoint_direction === 'consumer'){
    $("#div_consumer_host").hide();
    $("#div_consumer_port").hide();
    $("#div_consumer_file_path").hide();
    $("#div_consumer_file_scheme").hide();
    $("#div_consumer_username").hide();
    $("#div_consumer_pass").hide();
    $("#div_consumer_msg_types").hide();  
  }
  
}

