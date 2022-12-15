$(document).ready(function() {
  $(function () {
    let path = window.location.pathname.split('/').slice(0,4).join('/');
    if(path.charAt(path.length-1) !== '/'){
      path = path+'/';
    }
    //let path = window.location.pathname;
    //alert(path);
    let anchorElement = $("nav a.nav-link[href='"+path+"']");
    //alert(anchorElement.length);
    let ul_parent = anchorElement.parent("li").parent("ul");
    //alert(anchorElement.attr('href'));
    //alert(ul_parent.attr('class'));
    //alert('hasClass:'+ul_parent.attr('class').includes('nav-treeview').toString());
    if(ul_parent.attr('class').includes('nav-treeview')){
      //alert('in if parent nav-treeview');
      //alert(ul_parent.toString());
      ul_parent.parent("li").addClass('menu-open');
      //ul_parent.parent("li").children("a").addClass('active');
    }
    
    anchorElement.addClass('active');
    //alert(ul_parent.parent("li").attr('class'));
    
  });
});