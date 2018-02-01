var app = {
  /**
   * set app state for scenario type
   * init a scenario type
   * @param {string} type value from data-attr on html element
   */
  setState: function(type) {
    app.state.scenarioType = type;
    app.init[type]();
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

app.init = {
  'select': function() {
    console.log('%cinit stream segment selection scenario type', 'font-weight: bold;');
    // TODO get bbox from map window and assign to var
    var bbox = [-13406452.813644003, 6045242.123841717, -13403748.852081062, 6047669.009725289];
    app.request.get_segment_by_bbox(bbox)
      .then(function(data) {
        app.map.layer.streams.init(data);
      })
      .then(function() {
        app.map.interaction.select.segment();
      })
      .then(function() {
        console.log('%clistening for stream segement selection...', 'color: orange;');
      })
      .catch(function(data) {
        console.warn('failed to add map layer');
      });
  },
  'filter': function() {
    app.map.addLayer(app.map.layer.huc10);
  },
  'draw': function() {

  },
}

app.nav = {
  state: 'tall',
  short: function() {
    $('.nav-wrap').addClass('icons-only');
    $('.map-wrap').addClass('short-nav');
    $('.overlay').addClass('fade-out');
    setTimeout(function() {
      $('#scenario-nav').addClass('justify-content-start');
      $('#scenario-nav').removeClass('justify-content-center');
      $('#scenario-nav .col').each(function(i) {
        $(this).addClass('col-2');
      })
      $('.overlay').addClass('d-none');
    }, 1000);
  },
  tall: function() {
    $('.nav-wrap').removeClass('icons-only');
    $('.nav-wrap').removeClass('short-nav');
    setTimeout(function() {
      $('#scenario-nav').removeClass('justify-content-start');
      $('#scenario-nav').addClass('justify-content-center');
      $('#scenario-nav .col').each(function(i) {
        $(this).removeClass('col-2');
      })
    }, 1000);
  },
}

// TODO rewrite panel object
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
    $('#right-panel').css('height', appState.panel.height);
  },
  setPosition: function() {
    if (appState.panel.position == 'left') {
      $('#right-panel').css('right', 'auto');
      $('#right-panel').css('left', '0');
    } else if (appState.panel.position == 'right') {
      $('#right-panel').css('left', 'auto');
      $('#right-panel').css('right', '0');
    }
  },
  setContent: function() {
    $('.content').html(appState.panel.content);
  },
  setPanel: function(content, position, height) {
    appState.scenarioPanelContent   = content;
    appState.scenarioPanelPosition  = position;
    appState.scenarioPanelHeight    = height;
  },
  updatePanel: function() {
    scenarioTypePanel.showNextBtn();
    if (appState.panel.step > 1) {
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

app.request = {
  /**
   * get stream segments by bounding box
   * @param {Array} bbox coords from map view
   */
  get_segment_by_bbox: function(bbox) {
    // TODO get real bbox param
    return $.ajax({
      url: `/get_segment_by_bbox`,
      data: {
        bbox_coords: bbox
      },
      dataType: 'json'
    })
      .done(function(response) {
        console.log('%csuccessfully returned segments by bbox', 'color: green');
        return response;
      })
      .fail(function(response) {
        console.log('fail: ' + response);
        return false;
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
