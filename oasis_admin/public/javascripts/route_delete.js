$(document).ready(function () {
    $("a.route_delete").on("click", function () {
        let del = confirm('Delete route? This action can not be undone, are you sure?');
        if (del === true){
            alert('Route will be deleted!')
        } else {
            //alert('Route delete canceled!');
        }
        return del;
    });
});

    





