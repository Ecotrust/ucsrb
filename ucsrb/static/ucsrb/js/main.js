$(document).ready(function() {

  $('#scenario-nav a').click(function(event) {
    event.preventDefault();
    var type = event.target.dataset.scenarioType;
    var setScenarioType = new Promise((resolve,reject) => {
      appState.setScenarioType = type;
      // add error check
      resolve();
    });
    setScenarioType.then(function() {
      $('#map').css('background-color', '#aaa');
      $('#map').html(appState.scenarioType);
      if (appState.scenarioType === 'select') {
        $('#map').click(function() {
          fetch(scenarioTypeRequest.get_segment_by_id(1))
            .then(function(data) {
              $('#map').html(data.pourpoints);
            })
            .then(function(data) {
              scenarioTypePanel.setPanel(data, 'right', '50%');
            })
            .then(function(data) {
              scenarioTypePanel.updatePanel();
            });
        });
      }
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
