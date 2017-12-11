$(document).ready(function() {

  $('#scenario-nav a').click(function(event) {
    event.preventDefault();
    var setScenarioType = new Promise((resolve,reject) => {
      scenarioType.current = event.target.dataset.scenarioType;
      // add error check
      resolve();
    });
    setScenarioType.then(function() {
      $('#map').css('background-color', '#aaa');
      $('#map').html(scenarioType.current);
      scenarioTypePanel.step = 1;
      scenarioTypePanel.setPanel('right', '50%', scenarioType.current);
      scenarioTypePanel.updatePanel();
    });
  })

  $('.step-controls a').click(function(event) {
    event.preventDefault();
    var setScenarioStep = new Promise((resolve,reject) => {
      if (event.target.dataset.step == 'next') {
        scenarioTypePanel.step = scenarioTypePanel.step + 1;
      } else if (event.target.dataset.step == 'prev') {
        scenarioTypePanel.step = scenarioTypePanel.step - 1;
      } else {
        reject();
      }
      resolve();
    });
    setScenarioStep.then(function() {
      if (scenarioTypePanel.step == 2) {
        scenarioTypePanel.setPanel('right', '75%', 'step 2');
      } else if (scenarioTypePanel.step == 3) {
        scenarioTypePanel.setPanel('left', '100%', 'step 3');
      } else if (scenarioTypePanel.step === 4) {
        scenarioTypePanel.setPanel('right', '100%', `<button onclick="results()">Submit</button>`);
      } else if (scenarioTypePanel.step > 0) {
        scenarioTypePanel.setPanel('right', '100%', scenarioType.current);
      } else {
        scenarioTypePanel.setPanel('right', '50%', '');
      }
      scenarioTypePanel.updatePanel();
    })
    setScenarioStep.then(function() {
      $('.content').html(scenarioTypePanel.content);
    })
  });

});
