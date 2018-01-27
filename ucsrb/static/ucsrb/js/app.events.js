$(document).ready(function() {
  $('#scenario-nav button').click(function(event) {
    app.setState(event.currentTarget.dataset.scenarioType)
    $('#scenario-nav').addClass('icons-only');
    $('#scenario-nav').removeClass('col-9');
    $('#scenario-nav').addClass('col-4');
    $(`<div class="col-5"></div>`).insertAfter('#scenario-nav');
    $('#file-nav').addClass('less-padding');
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
