$(document).ready(function () {
  $("form").submit(function (event) {
    let freq_type = $("#freq_type").val();
    let sub_day = $("#sub_day_freq_type").val();
    let spec_time = $("#spec_time").val();
    let spec_date = $("#spec_date").val();
    //if daily, weekly, monthly or yearly we must have a spec time
    let spec_time_required = 'Daily, Weekly, Monthly, Monthly_Weekly or Yearly that do not have a sub day schedule require a Specific Time to be set!';
    let spec_time_and_date_required = 'Specific Date and Time Fields must be filled out for this Frequency Type!';
    let spec_date_required = 'Specific Date required, for Yearly only day and month are used.';
    if(freq_type === 'Daily' || freq_type === 'Weekly' || freq_type === 'Monthly' || freq_type === 'Monthly_Weekly'){
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
  $("#freq_type").on('change', function () {
    showSelected();
  });
  $("#sub_day_freq_type").on('change', function () {
    showSubDaySelected();
  });
  $("#div_multi_times_count").on('change', function () {
      let count = $("#multi_time_count").val();
      $("#div_multi_spec_time input").remove();
      //add show count number of spec_times and hide default
      //alert(count);
    $("#div_multi_spec_time").append('<br/>');
      for(let x=0;x<count;x++){
        $("#div_multi_spec_time").append('<span class="col-form-label-sm">Specific Time '+(x+1)+'</span> <input class="form-control" name="spec_time_'+(x+1)+'" id="spec_time_'+(x+1)+'" type="time">');
      }
      $("#div_multi_spec_time").show();
      $("#div_spec_time").hide();
  });
  hideAll();
  showSelected();
  subhideAll();
  showSubDaySelected();
});
function showSubDaySelected() {
  //alert($("#sub_day_freq_type").val());
  subhideAll();
  switch ($("#sub_day_freq_type").val()) {
    case "None":
      let ft = $("#freq_type").val();
      if(ft === 'Daily' || ft === 'Weekly' || ft === 'Monthly' || ft === 'Yearly'){
        $("#div_spec_time").show();
      }
      break;
    case "Minutes":
      $("#div_sub_day_freq_interval_minutes").show();
      $("#div_sub_day_start_time").show();
      $("#div_sub_day_end_time").show();
      $("#div_sub_day_stop_schedule").show();
      $("#div_spec_time").hide();
      
      break;
    case "Hours":
      $("#div_sub_day_freq_interval_hours").show();
      $("#div_sub_day_start_time").show();
      $("#div_sub_day_end_time").show();
      $("#div_sub_day_stop_schedule").show();
      $("#div_spec_time").hide();
      break;
   /* case "Specific_Time":
      $("#div_spec_time").show();
      break;*/
  }
}
function showSelected() {
  //alert('running showselected function');
  hideAll();
  switch ($("#freq_type").val()) {
    case "Specific_Date_and_Time":
      $("#div_spec_date").show();
      $("#div_spec_time").show();
      break;
    /* All daily now requires spec time
      case "Specific_Time_Daily":
      $("#div_spec_time").show();
      break;*/
    case "Minutes":
      $("#div_freq_interval_minutes").show();
      $("#div_spec_time").hide();
      break;
    case "Hours":
      $("#div_freq_interval_hours").show();
      $("#div_spec_time").hide();
      break;
    case "Daily":
      $("#div_freq_interval_days").show();
      $("#div_spec_time").show();
      $("#div_sub_day_freq_type").show();
      $("#div_sub_day_freq_interval").show();
      break;
    case "Multi Times a Day":
      $("#div_freq_interval_days").show();
      $("#div_multi_times_count").show();
      $("#div_spec_time").show();
      //multi times a day option would never have sub days
      $("#div_sub_day_freq_type").hide();
      $("#div_sub_day_freq_interval").hide();
      break;
    case "Weekly":
      $("#div_freq_interval_weekly").show();
      $("#div_spec_time").show();
      $("#div_sub_day_freq_type").show();
      $("#div_sub_day_freq_interval").show();
      break;
    case "Multi Day Of Week":
      //same as day of week we just save multiple and let select multiple weekdays
      //so we hide dropdown of day of week
      $("#div_freq_interval_weekly").hide();
      //we show multi-select
      $("#div_multi_freq_interval_weekly").show();
      $("#div_spec_time").show();
      $("#div_sub_day_freq_type").show();
      $("#div_sub_day_freq_interval").show();
      break;
    case "Monthly":
      $("#div_freq_interval_monthly").show();
      $("#div_spec_time").show();
      $("#div_sub_day_freq_type").show();
      $("#div_sub_day_freq_interval").show();
      break;
    case "Monthly_Weekly":
      $("#div_freq_interval_monthly_weekly").show();
      $("#div_sub_freq_interval_monthly_weekly").show();
      $("#div_spec_time").show();
      $("#div_sub_day_freq_type").show();
      $("#div_sub_day_freq_interval").show();
      break;
    case "Yearly":
      $("#div_spec_time").show();
      $("#div_spec_date").show();
      $("#div_sub_day_freq_type").show();
      $("#div_sub_day_freq_interval").show();
    default:
      //do nothing
  }
}

function hideAll() {
  $("#div_freq_interval_minutes").hide();
  $("#div_freq_interval_hours").hide();
  $("#div_freq_interval_days").hide();
  $("#div_freq_interval_weekly").hide();
  $("#div_multi_freq_interval_weekly").hide();
  $("#div_freq_interval_monthly").hide();
  $("#div_spec_date").hide();
  $("#div_spec_time").hide();
  $("#div_multi_times_count").hide();
  $("#multi_time_count").val(1);
  $("#div_multi_spec_time").hide();
  $("#div_sub_day_freq_type").hide();
  $("#div_freq_interval_monthly_weekly").hide();
  $("#div_sub_freq_interval_monthly_weekly").hide();
  subhideAll();
}

function subhideAll() {
  $("#div_sub_day_freq_interval").hide();
  $("#div_sub_day_freq_interval_hours").hide();
  $("#div_sub_day_freq_interval_minutes").hide();
  $("#div_sub_day_start_time").hide();
  $("#div_sub_day_end_time").hide();
  $("#div_sub_day_stop_schedule").hide();
}