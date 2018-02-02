var app = {
  /**
   * set app state for process method
   * init a process method
   * @param {string} method value from data-attr on html element
   */
  setState: function(method) {
    app.state.setMethod = method;
    app.init[method]();
  },
}

app.init = {
  'select': function() {
    // app.request.get_viewer_select();
    app.request.get_filter_form()
        .then(function(data) {
            app.state.panelContent = data // set panel state
        })
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
  setState: function(height) {
    app.state.navHeight = height;
  },
  short: function() {
    app.state.navHeight = 'short'; // set state
    // style nav
    $('.nav-wrap').addClass('icons-only');
    $('.map-wrap').addClass('short-nav');
    $('.overlay').addClass('fade-out');
    setTimeout(function() {
      $('#process-nav').addClass('justify-content-start');
      $('#process-nav').removeClass('justify-content-center');
      $('#process-nav .col').each(function(i) {
        $(this).addClass('col-2');
      })
      $('.overlay').addClass('d-none');
    }, 1000);
  },
  tall: function() {
    app.state.navHeight = 'tall'; // set state
    $('.nav-wrap').removeClass('icons-only');
    $('.nav-wrap').removeClass('short-nav');
    setTimeout(function() {
      $('#process-nav').removeClass('justify-content-start');
      $('#process-nav').addClass('justify-content-center');
      $('#process-nav .col').each(function(i) {
        $(this).removeClass('col-2');
      })
    }, 1000);
  },
}

app.panel = {
    setRPanelContent: function() {
        $('#right-panel').html(app.state.panelContent);
    }
}

/*
 * Application AJAX requests object and methods
 * {get_segment_by_bbox} segment by bounding box
 * {get_segment_by_id} segment by id
 * {get_pourpoint_by_id} pourpoint by id
 * {filter_results} filter results
 *
 */
app.request = {
  get_viewer_select: function() {
    // return $.ajax({
    //     url: `/viewer/select`,
    //     dataType: 'html',
    //   });
  },
  /**
   * get scenario filter form from scenario model
   * @return {[html]} [form html template]
   */
  get_filter_form: function() {
    return $.ajax({
        url: `/features/treatmentscenario/form`,
        dataType: 'html',
      })
      .done(function(response) {
        console.log('%csuccessfully returned filter form', 'color: green');
        return response;
      })
  },
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
        console.log(`%cfail: ${response}`, 'color: red');
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
        console.log(`%cfail: ${response}`, 'color: red');
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
        console.log(`%cfail: ${response}`, 'color: red');
      });
  },
  get_basin: function(pp_id) {
    $.ajax({
      url: '/viewer/select/get_basin',
      data: {
        pourPoint: pp_id,
      },
      dataType: 'json',
      success: function(response) {
        console.log(`%csuccess: got basin`, 'color: green');
        return response;
      },
      error: function(response, status) {
        console.log(`%cfail: ${response}`, 'color: red');
        return status;
      }
    })
  },
  filter_results: function(pourpoint) {
    $.ajax({
       url: "/api/filter_results",
       data: {
         ppid: pourpoint
       },
     })
  },
  saveState: function() {
    $.ajax({
      url: '/sceanrio/treatmentscenario/save',
      type: 'POST',
      data: app.state,
      dataType: 'json',
      success: function(response, status) {
        console.log(`%csuccess: ${response}`, 'color: green');
        return status;
      },
      error: function(response, status) {
        console.log(`%cfail: ${response}`, 'color: red');
        return status;
      }
    })
  }
}
