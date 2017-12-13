var appState = {
  scenarioType: 0,
  scenarioPanel: {
    content: '',
    position: '',
    panelHeight: '',
    step: 0
  },
  get scenario_type() {
    return this.scenarioType;
  },
  set setScenarioType(type) {
    this.scenarioType = type;
  },
  get get_scenarioPanel() {
    return this.scenarioPanel;
  },
  set scenarioPanelContent(content) {
    this.scenarioPanel.content = content;
  },
  set scenarioPanelPosition(position) {
    this.scenarioPanel.position = position;
  },
  set scenarioPanelHeight(height) {
    this.scenarioPanel.height = height;
  }
}

var scenarioType = {
  showPourPoints: function(data) {

  }
}

var scenarioTypePanel = {
  showNextBtn: function() {
    $('#next-step').addClass('show');
  },
  showPrevBtn: function() {
    $('#prev-step').addClass('show');
  },
  hideNextBtn: function() {
    $('#next-step').removeClass('show');
  },
  hidePrevBtn: function() {
    $('#prev-step').removeClass('show');
  },
  setHeight: function() {
    $('#right-panel').css('height', appState.scenarioPanel.height);
  },
  setPosition: function() {
    if (appState.scenarioPanel.position == 'left') {
      $('#right-panel').css('right', 'auto');
      $('#right-panel').css('left', '0');
    } else if (appState.scenarioPanel.position == 'right') {
      $('#right-panel').css('left', 'auto');
      $('#right-panel').css('right', '0');
    }
  },
  setContent: function() {
    $('.content').html(appState.scenarioPanel.content);
  },
  setPanel: function(content, position, height) {
    appState.scenarioPanelContent   = content;
    appState.scenarioPanelPosition  = position;
    appState.scenarioPanelHeight    = height;
  },
  updatePanel: function() {
    scenarioTypePanel.showNextBtn();
    if (appState.scenarioPanel.step > 1) {
      scenarioTypePanel.showPrevBtn();
    } else {
      scenarioTypePanel.hidePrevBtn();
    }
    scenarioTypePanel.setHeight();
    scenarioTypePanel.setPosition();
    scenarioTypePanel.setContent();
  }
};

var scenarioTypeCall = {
  /**
   * Request stream segement by id
   * @param {number|int} id
   * Returns stream segement Object
   * @returns {Object} segment
   * @property {string} name
   * @property {int} id
   * @property {geojson} geometery
   * @property {Array} pourpoints
       * @property {Object|id,geometry,name} list of objects
   */
  get_segment_by_id: function(id) {
    let request = 'segment/' + id;
    return $.ajax(request)
      .done(function(response) {
        console.log(response);
        return response;
      })
      .fail(function(response) {
        console.log('fail: ' + response);
      });
  },
  /**
   * Request pourpoint by id
   * @param {number|int} id
   * Returns pourpoint Object
   * @returns {Object} pourpoint
   * @property {string} name
   * @property {number} id
   * @property {number} acres
   * @property {Object} point_geometry
   * @property {Object} area_geometry
   */
  get_pourpoint_by_id: function(id) {
    let request = 'pourpoint/' + id;
    return $.ajax(request)
      .done(function(response) {
          console.log(response);
      });
  }
}
