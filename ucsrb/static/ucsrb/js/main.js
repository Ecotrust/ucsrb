$(document).ready(function() {
  $('#scenario-nav a').click(function(event) {
    event.preventDefault();
    let setScenarioType = new Promise((resolve,reject) => {
      scenarioType.current = event.target.dataset.scenarioType;
      // add error check
      resolve();
    });
    setScenarioType.then(function() {
      $('.step1').addClass('show');
    })
  })
})
