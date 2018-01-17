$(document).ready(function() {
  $('#scenario-nav button').click(function(event) {
    console.log(event.currentTarget);
    app.setState(event.currentTarget.dataset.scenarioType)
  });
  $('.step-controls a').click(function(event) {
    app.setStep(event.target.dataset.step);
  });
});

// ------ TODO update or delete below
// currently saving below for reference

app.selectOption = function(scenario) {
  setScenarioType.then(function() {
    $('#map').append('<button class="segment">A stream segment</button><h2>Open in Dev tools</h2>')
      .find('button')
      .click(function(event) {
        $(event.target).remove();
        var getSegment = new Promise((resolve,reject) => {
          var segment = scenarioTypeRequest.get_segment_by_id(1);
          // add error check
          resolve(segment);
        });
        getSegment.then(function(segment) {
          for (let i = 0; i < segment.pourpoints.length; i++) {
            var $btn = $(`<button class="pourpoint" data-id="${segment.pourpoints[i].id}">${segment.pourpoints[i].name}</button>`);
            $btn.data('id', segment.pourpoints[i].id)
            $btn.bind('click', function(event) {
              var getPourPoint = new Promise((resolve,reject) => {
                var pourpoint = scenarioTypeRequest.get_pourpoint_by_id(event.target.dataset.id)
                resolve(pourpoint);
              });
              getPourPoint.then(function(pourpoint) {
                $('#map').html('<div style="background: darkslateblue; color:#fff; height: 200px; width: 200px; position: relative;">Basin</div>');
                var panelContent = '<h1>Filters</h1><button id="filter">Filter</button>';
                scenarioTypePanel.setPanel(panelContent, 'right', '50%');
                scenarioTypePanel.updatePanel();
                app.listenBeginEval();
              });
            });
            $('#map').append($btn)
          }
          scenarioTypePanel.setPanel(segment.name, 'right', '50%');
          scenarioTypePanel.updatePanel();
        })
      });
  });
}



app.listenBeginEval = function() {
  $('#right-panel div:last-of-type').addClass('show');
  $('#right-panel').find('button').click(function() {
    console.log('filter');
    $('#map div').animate({
      left: 400,
      height: '300px',
      opacity: .5,
      width: '400px',
      top: 150
    }, 1200 );
    $('#map div').text('filtering');
    setTimeout(function() {
      $('#map div').animate({
        opacity: 1,
        top: 100
      }, 600 );
      $('#map div').text('filtered');
    }, 1600)
  });
  $('#begin-evaluation').click(function(event) {
    event.preventDefault();
    scenarioTypePanel.setPanel('Results!!!', 'right', '50%');
    scenarioTypePanel.updatePanel();
    $('#right-panel').animate({
      height: '600px',
      opacity: 0.8,
      boxShadow: '0 0 10px #333',
    }, 600);
  });
}


app.setStep = function(step) {
  var setScenarioStep = new Promise((resolve,reject) => {
    if (step == 'next') {
      scenarioTypePanel.step = scenarioTypePanel.step + 1;
    } else if (step == 'prev') {
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
}
