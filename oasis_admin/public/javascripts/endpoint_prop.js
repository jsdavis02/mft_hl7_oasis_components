$(document).ready(function () {
    $("#div_new_key").hide();
    $("div.alert-info").hide();
    var n = $("#name").val();
    $('#'+n).show();
    $("#name").on('change', function () {
        $("div.alert-info").hide();
        $('#'+$(this).val()).show();
        if ($(this).val() === 'Add New') {
            $("#div_new_key").show();
        } else {
            $("#div_new_key").hide();
        }
    });
});
    