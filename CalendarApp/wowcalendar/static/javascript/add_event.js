function populateFields() {
  var selectedId = document.getElementById("template_select").value;
  // Make an AJAX call to the server to fetch the data
  $.ajax({
    url: '/home/template/data',
    type: 'GET',
    data: {'template_id': selectedId},
    success: function(data) {
      // Update the input fields with the data
      $('#name').val(data.name);
      $('#description').val(data.description);
      $('#start-time').val(data.start_time);
      $('#end-time').val(data.end_time);
      $('#deadline').val(data.deadline);
    },
    error: function(xhr, status, error) {
      console.log("error");
    }
  });
}