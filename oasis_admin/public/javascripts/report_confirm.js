$(document).ready(function () {
    $("a.confirm_report").on("click", function () {
        let report = confirm('Are you sure you want to report an issue with this file transfer?');
        if (report === true){
            alert('Issue will be reported!')
        } else {
            //alert('Issue will not be reported!');
        }
        return report;
    });
});
    



