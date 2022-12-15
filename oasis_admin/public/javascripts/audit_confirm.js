$(document).ready(function () {
    $("a.mft_resend").on("click", function () {
        let resend = confirm('Do you want to resend this file?');
        if (resend === true){
            //alert('File will be resent!')
        } else {
            //alert('Schedule Delete canceled!');
        }
        return resend;
    });
    
    $("a.resend_confirm").on("click", function (event) {
        let id = $(this).attr('pk');
        let edit = confirm('Do you want to edit the payload?');
        if (edit) {
            event.preventDefault();
            window.location.href = '/audit/payload_edit?action=resend&id='+id;
        } else {
            alert('Click OK to resend message.');
        }
    });
    
    $("a.reproc_confirm").on("click", function (event) {
        let id = $(this).attr('pk');
        let edit = confirm('Do you want to edit the payload?');
        if (edit) {
            event.preventDefault();
            window.location.href = '/audit/payload_edit?action=reprocess&id='+id;
        } else {
            alert('Click OK to reprocess message.');
        }
    });
});
    





