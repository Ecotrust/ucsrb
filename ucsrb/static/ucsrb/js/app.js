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

scenario_type_selection_made = function(selectionType) {
  var extent = new ol.extent.boundingExtent([[-121.1, 47], [-119, 49]]);
  extent = ol.proj.transformExtent(extent, ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
  if (selectionType == 'select') {
    app.map.getView().animate({zoom: 10, center: [(extent[0]+extent[2])/2, (extent[1]+extent[3])/2]});
  } else {
    app.map.zoomToExtent(extent);
  }
}

app.init = {
    'select': function() {
        app.map.clearLayers();
        app.state.step = 0;
        app.map.selection.setSelect(app.map.selection.selectSelectSingleClick);
        app.map.enableLayer('streams');
        scenario_type_selection_made('select');
    },
    'filter': function() {
        app.map.clearLayers();
        app.state.step = 0;
        app.map.selection.setSelect(app.map.selection.selectFilterSingleClick);
        app.map.enableLayer('huc12');
        scenario_type_selection_made('filter');
    },
    'draw': function() {
      // enable drawing
      app.map.clearLayers();
      app.state.step = 0;
      app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
      scenario_type_selection_made('draw');
      //TODO: trigger this with button or something once user has navigated
      app.map.interaction.draw.init();
    }
}

initFiltering = function() {
  setTimeout(function() {
    if ($('#focus_area_accordion').length > 0) {
      $('#id_focus_area').prop('checked', true);
      $('#id_focus_area_input').val(app.state.focusAreaState.id);
      $('#focus_area_accordion').hide();
      app.viewModel.scenarios.scenarioFormModel.toggleParameter('focus_area');
    } else {
      initFiltering();
    }
  }, 100);
};

app.panel = {
    form: {
        init: function() {
            app.map.layer.planningUnits.init();
            app.map.layer.scenarios.init();
            app.viewModel.scenarios.createNewScenario('/features/treatmentscenario/form/');
            initFiltering();
        },
    }
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
        $('.overlay').addClass('fade-out short-overlay');
        setTimeout(function() {
            $('#process-nav').addClass('justify-content-start');
            $('#process-nav').removeClass('justify-content-center');
            $('#process-nav .col').each(function(i) {
                $(this).addClass('col-2');
            })
            $('.overlay').removeClass('fade-out');
            app.state.step = 0;
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
    instructions: {
        select: [
            'Select the stream segment where you want to see changes in flow',
            'Select specific point along stream reach to evaluate changes in flow associated with management activity upstream',
            'Select filters to narrow your treatment region',
        ],
        filter: [
            'Select forest unit to filter',
            'Select filters to narrow your treatment area',
        ],
        draw: [
            'Click on the map to start drawing your management area',
            'Add additional points then double-click to finish; Re-select point to edit'
        ],
    },
    stepActions: {
      select: [
        false,
        false,
        app.panel.form.init
      ],
      filter: [
        false,
        app.panel.form.init
      ],
      draw: [
        false,    //TODO: enable drawing
        false     //TODO: ??? enable editing?
      ]
    }
}

app.panel = {
    moveLeft: function() {
        app.panel.element.classList.add('left');
        app.panel.element.classList.remove('right');
        app.state.panel.position = 'left'; // set state
    },
    moveRight: function() {
        app.panel.element.classList.add('right');
        app.panel.element.classList.remove('left');
        app.state.panel.position = 'right'; // set state
    },
    setContent: function(content) {
        app.state.panel.content = content;
        app.panel.element.innerHTML = content;
    },
    form: {
        init: function() {
            app.viewModel.scenarios.createNewScenario('/features/treatmentscenario/form/');
        },
    },
    results: {
        element: function() {
            return document.querySelector('#results');
        },
        init: function(id) {
            app.panel.moveLeft();
            app.request.get_results(id)
                .then(function(response) {
                    app.panel.results.addAggPanel(response);
                    app.panel.results.addHydroPanel(response);
                })
                .catch(function(response) {
                    console.log('%c failed to get results: %o', 'style: salmon;', response);
                });
        },
        addAggPanel: function(content) {
            var html = `<section class="aggregate result-section">`;
                html += `<div class="media">
                            <img class="align-self-center mr-3" src="/static/ucsrb/img/icon/i_pie_chart.svg" alt="aggregate">
                            <div class="media-body">
                                <h4 class="mt-0">Aggregate</h4>
                            </div>
                            <a id="expand" href="" id="expand" /><img class="align-self-top ml-3" src="/static/ucsrb/img/icon/i_expand.svg" alt="expand" /></a>
                         </div>`;
                html += `<div class="feature-result"><span class="lead">${content.aggregate_results.forest_types.forest_totals}</span> acres</div>`
                html += `<div class="result-list-wrap">
                            <h5>Forest Management</h5>`;
                        html += app.panel.results.styleObject(content.aggregate_results.forest_types);
                    html += '<h5>Landforms/Topography</h5>';
                        html += app.panel.results.styleObject(content.aggregate_results['landforms/topography']);
                    html += `<button class="btn btn-outline-primary">Download</button>
                        </div>`
             html += '</section>';
             app.panel.setContent(html);
        },
        addHydroPanel: function(content) {

        },
        styleObject: function(obj) {
            var html = '<dl class="row">';
            for (var key in obj) {
                html += `<dd class="col-sm-5">${obj[key]}</dd>
                         <dt class="col-sm-7">${key}</dt>`
            }
            html += '</dl>'
            return html;
        },
    },
    domElement: function() { // extra function for those who dont like js getters
        return this.element;
    },
    get element() {
        return document.querySelector('#panel');
    }
}

/**
 * Application AJAX requests object and methods
    * {get_results} results for treatment scenario
    * {get_segment_by_bbox} segment by bounding box
    * {get_segment_by_id} segment by id
    * {get_pourpoint_by_id} pourpoint by id
    * {filter_results} filter results
*
*/
app.request = {
    /**
     * get results for treatment scenario
     * @param  {[number]} id treatment scenario id [on scenario this is created]
     * @return {[json]} result data
     */
    get_results: function(id) {
        return $.ajax(`/get_results_by_scenario_id/${id}`)
            .done(function(response) {
                console.log('%csuccessfully returned result: %o', 'color: green', response);
            })
            .fail(function(response) {
                console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
            });
    },
    /**
    * Planning Units
    * scenario planning units to filter upon
    * @return {[json]} features list
    */
    get_planningunits: function() {
        return $.ajax('/scenario/get_planningunits')
            .done(function(response) {
                console.log('%csuccessfully returned planning units: %o', 'color: green', response);
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
            });
    },
    get_scenarios: function() {
        return $.ajax('/ucsrb/get_scenarios/')
            .done(function(response) {
                console.log('%csuccessfully got scenarios: %o', 'color: green', response);
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get scenarios: %o`, 'color: red', response);
            });
    },
    /**
    * get stream segments by bounding box
    * @param {Array} bbox coords from map view
    */
    get_segment_by_bbox: function(bbox) {
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
                console.log(`%cfail @ get segment by bbox: %o`, 'color: red', response);
                return false;
            });
    },
    /**
     * Request stream segement by id
     * @param {number|int} id
     * @returns {Object} stream segement
     * @property segment name id geometry pourpoints[id, geometry, name]
     */
    get_segment_by_id: function(id) {
        return $.ajax(`/segment/${id}`)
            .done(function(response) {
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ segment by id: %o`, 'color: red', response);
            });
    },
    /**
     * Request pourpoint by id
     * @param {number|int} id
     * @returns {Object} pourpoint
     * @property name id acres point_geometry area_geometry
     */
    get_pourpoint_by_id: function(id) {
        return $.ajax(`pourpoint/${id}`)
            .done(function(response) {
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get pourpoint id: %o`, 'color: red', response);
            });
    },
    get_focus_area: function(feature, layerName, callback) {
        props = feature.getProperties();
        id = props[app.mapbox.layers[props.layer].id_field];
        return $.ajax({
            url: '/ucsrb/get_focus_area',
            data: {
                id: id,
                layer: layerName,
            },
            dataType: 'json',
            success: function(response) {
                console.log(`%csuccess: got focus area`, 'color: green');
                app.state.setFocusArea = response;
                callback(feature, response.geojson);
            },
            error: function(response, status) {
                console.log(`%cfail @ get focus area: %o`, 'color: red', response);
                callback(null, response);
                return status;
            }
        })
    },
    get_focus_area_at: function(feature, layerName, callback) {
      /**
       * This is sloppy, but I don't know how to get the geometry from a VectorTile feature.
       * @todo {Priority low} find try and set geometry from vector tile
       */
      point = feature.b;
      return $.ajax({
          url: '/ucsrb/get_focus_area_at',
          data: {
              point: point,
              layer: layerName,
          },
          dataType: 'json',
          success: function(response) {
              console.log(`%csuccess: got focus area at point`, 'color: green');
              callback(feature, response);
          },
          error: function(response, status) {
              console.log(`%cfail @ get focus area at point: %o`, 'color: red', response);
              callback(null, response);
          }
      })
    },
    /**
     * get a pourpoint's basin
     * @param  {number} pp_id [id]
     * @return {[GeoJSON]} drainage basin
     */
    get_basin: function(feature, callback) {
      var pp_id = feature.getProperties().OBJECTID;
      return $.ajax({
        url: '/ucsrb/get_basin',
        data: {
          pourPoint: pp_id,
          // method: app.state.method,
        },
        dataType: 'json',
        success: function(response) {
          console.log(`%csuccess: got basin`, 'color: green');
          app.state.setFocusArea = response;
          callback(feature, response.geojson);
          return response;
        },
        error: function(response, status) {
          console.log(`%cfail @ get basin: %o`, 'color: red', response);
          // we don't have the ppt basins yet, just get a HUC12 for now.
          app.request.get_focus_area_at(feature, 'HUC12', function(feature, hucFeat) {
            vectors = (new ol.format.GeoJSON()).readFeatures(hucFeat.geojson, {
                dataProjection: 'EPSG:3857',
              featureProjection: 'EPSG:3857'
            });
            // set property id with hucFeat.id
            vector = vectors[0].getGeometry();
            vector.set('layer', 'huc12_3857');
            vector.set('HUC_12', hucFeat.id.toString());
            app.request.get_focus_area(vector, 'HUC12', callback);
          });
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
            data: app.saveState,
            dataType: 'json',
            success: function(response, status) {
                console.log(`%csuccess: ${response}`, 'color: green');
                return status;
            },
            error: function(response, status) {
                console.log(`%cfail @ save state: %o`, 'color: red', response);
                return status;
            }
        })
    }
}
