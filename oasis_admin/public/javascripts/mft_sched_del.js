$(document).ready(function () {
    $("a.mft_sched_delete").on("click", function () {
        let del = confirm('Delete MFT Schedule? This action can not be undone, are you sure?');
        if (del === true){
            //alert('Schedule will be deleted!')
        } else {
            //alert('Schedule Delete canceled!');
        }
        return del;
    });
});

    





