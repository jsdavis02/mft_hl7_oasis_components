$(document).ready(function () {
    $("a.delete").on("click", function () {
        let del = confirm('This action can not be undone, are you sure?');
        if (del === true){
            alert('User will be deleted!')
        } else {
            alert('Delete canceled!');
        }
        return del;
    });
    $("a.invite").on("click", function () {
        let inv = confirm('Email will be sent with password of "changeme" so make sure user password is set to "changeme"!');
        
        return inv;
    });
});

    





