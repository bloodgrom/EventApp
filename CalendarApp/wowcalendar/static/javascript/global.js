// $(document).ready(function() {
//   // show the alert
//   setTimeout(function() {
//       $(".alert").alert('close');
//   }, 2000);
// });

$(document).ready(function() {
    // show the alert
    setTimeout(function() {
      $(".alert").slideUp(500, function() {
        $(this).remove();
    });
    }, 1500);
});
