$(document).ready(function() {
  $('#scenario-nav button').click(function(event) {
    app.setState(event.currentTarget.dataset.scenarioType)
    $('.nav-wrap').addClass('icons-only');
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
