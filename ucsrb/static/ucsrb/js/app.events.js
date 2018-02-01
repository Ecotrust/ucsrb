$(document).ready(function() {
  $('#scenario-nav button').click(function(event) {
    app.setState(event.currentTarget.dataset.scenarioType);
    app.nav.state = 'short';
    app.nav.short();
    setTimeout(function() {
      $('#scenario-nav button').each(function() {
        $(this).removeClass('active');
      })
      event.target.classList.add('active');
    }, 1000);
  });
  /**
   * for panel
   * @param  {[type]} event [description]
   * @return {[type]}       step
   */
  $('.step-controls a').click(function(event) {
    app.setStep(event.target.dataset.step);
  });
});
