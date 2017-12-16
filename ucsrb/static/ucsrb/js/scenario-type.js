var appState = {
  scenarioType: 0,
  scenarioPanel: {
    content: '',
    position: '',
    panelHeight: '',
    step: 0
  },
  /**
   * init scenario type
   * invoked by getter `scenario_type` for appState
   * @param {Object} self should be the appState object
   * @param {string} type set in data-attr on element
   */
  initScenario: function(self, type) {
    self.scenarioType = type;
    switch (type) {
      case 'select':
        scenarioType.initStreamSelectScenario();
        break;
      case 'filter':
        break;
      default:
        break;
    }
  },
  get scenario_type() {
    return this.scenarioType;
  },
  /**
   * setter for scenario type
   * @param {string} type set in data-attr on element
   */
  set setScenarioType(type) {
    this.initScenario(this,type);
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
  initStreamSelectScenario: function() {
    // TODO get bbox from map window and assign to var
    var bbox = [-13406452.813644003, 6045242.123841717, -13403748.852081062, 6047669.009725289];
    var getStreamSegments = new Promise((resolve,reject) => {
      scenarioTypeRequest.get_segment_by_bbox(bbox);
    });
    getStreamSegments.then(function(data) {
      $('#map').append(data);
    });
    // TODO add to map streams
  },
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
  },
  beginEvaluation: function() {
    
  }
};

var scenarioTypeRequest = {
  /**
   * get stream segments by bounding box
   * @param {Array} bbox coords from map view
   */
  get_segment_by_bbox: function(bbox) {
    // TODO get real bbox param
    $.ajax({
      url: `/api/get_segment_by_bbox`,
      data: {
        bbox_coords: bbox
      },
      dataType: 'json'
    })
      .done(function(response) {
        return response;
      })
      .fail(function(response) {
        console.log('fail: ' + response);
      });
  },
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
    return $.ajax(`/segment/${id}`)
      .done(function(response) {
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
    return $.ajax(`pourpoint/${id}`)
      .done(function(response) {
          return response;
      })
      .fail(function(response) {
        console.log('fail: ' + response);
      });
  },
  filter_results: function(pourpoint) {
    $.ajax({
       url: "/api/filter_results",
       data: {
         ppid: pourpoint
       }
     })
  }
}
