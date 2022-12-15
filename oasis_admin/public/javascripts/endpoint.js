$(document).ready(function () {
  $("#add_route").hide();
  $("a.delete").click(function (e) {
    e.preventDefault();
    let dellink = this.href;
    //alert(this.href);
    $('#delModal').modal('show');
    $('#yes-del').click(function () {
      $('#delModal').modal('hide');
      window.location.replace(dellink);
      //alert(dellink);
    });
    $('#no-del').click(function () {
      //remove onclick
      $('#yes-del').prop("onclick", null).off("click");
    });
  });
  $("input.form-check-inline").click(function (e) {
    //see if we have a consumer and producer checked on page and if so show link url and reset url for route
    let check_count = $("input:checked").length;
    //alert(check_count);
    if(check_count == 2){
      let btn = $("#add_route");
      let parms = '';
      $("input:checked").each(function () {
        parms += $(this).attr('e_dir')+'_id='+$(this).attr('e_id')+'&';
      });
      //alert(parms);
      btn.attr('href', btn.attr('href')+parms);
      btn.show();
    }
  });
});
    