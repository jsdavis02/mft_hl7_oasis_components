$(document).ready(function () {
    $("#div_new_key").hide();
    $("#lookup_key").on('change', function () {
        if ($(this).val() === 'Add New') {
            $("#div_new_key").show();
        } else {
            $("#div_new_key").hide();
        }
    });
});
    