$(document).ready(function() {
  $('#process-nav button').click(function(event) {
    app.setState(event.currentTarget.dataset.method);
    app.nav.short();
    setTimeout(function() {
      $('#process-nav button').each(function() {
        $(this).removeClass('active');
      })
      event.target.classList.add('active');
    }, 1000);
  });
});
