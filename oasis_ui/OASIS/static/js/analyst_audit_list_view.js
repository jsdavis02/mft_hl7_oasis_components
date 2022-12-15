// Call the dataTables jQuery plugin
$(document).ready(function() {
  $(function () {
    $('[data-toggle="tooltip"]').tooltip(
        {
          container: 'body'
        }
    )
  });
  $('#audTable').DataTable({
    paging: false,
    searching: true,
    "language": {
      "search": "Search Page"
    }
  });
});
