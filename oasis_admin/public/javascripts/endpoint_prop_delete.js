$(document).ready(function () {
    $("a.prop_delete").on("click", function () {
        let del = confirm('This action can not be undone, are you sure?');
        if (del === true){
            alert('End Point Property will be deleted!')
        } else {
            alert('Delete canceled!');
        }
        return del;
    });
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
});

    





