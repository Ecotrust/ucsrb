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
    scenarioInProgress: function() {
        if (app.state.step === 0 || app.state.method === 'reset') {
            return false;
        } else {
            return true;
        }
    },
    promptToSave: function() {
        console.log('Save before starting over?');
    }
}

scenario_type_selection_made = function(selectionType) {
  var extent = new ol.extent.boundingExtent([[-121.1, 47], [-119, 49]]);
  extent = ol.proj.transformExtent(extent, ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
  if (selectionType == 'select') {
    app.map.removeInteraction(app.map.draw.draw);
    app.map.layer.draw.layer.setVisible(false);
    app.map.getView().animate({zoom: 10, center: [(extent[0]+extent[2])/2, (extent[1]+extent[3])/2]});
    app.map.addInteraction(app.map.Pointer);
  } else if (selectionType == 'filter'){
    app.map.removeInteraction(app.map.draw.draw);
    app.map.layer.draw.layer.setVisible(false);
    app.map.addInteraction(app.map.Pointer);
    app.map.zoomToExtent(extent);
  } else {
    app.map.layer.draw.layer.setVisible(true);
    app.map.removeInteraction(app.map.Pointer);
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
      app.map.clearLayers();
      app.state.step = 0;
      app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
      scenario_type_selection_made('draw');
    },
    'hydro': function() {
        app.panel.results.showHydro();
    },
    'aggregate': function() {
        app.panel.results.showAggregate();
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

drawingIsSmallEnough = function(areaInMeters) {
  maxAcres = app.map.draw.maxAcres;
  metersPerAcre = 4046.86;
  return maxAcres*metersPerAcre > areaInMeters;
}

app.panel = {
    hide: function() {
      app.panel.element.hidden = true;
    },
    show: function() {
      app.panel.element.hidden = false;
    },
    moveLeft: function() {
        app.panel.show();
        app.panel.getElement.classList.add('left');
        app.panel.getElement.classList.remove('right');
        app.state.panel.position = 'left'; // set state
    },
    moveRight: function() {
        app.panel.show();
        app.panel.getElement.classList.add('right');
        app.panel.getElement.classList.remove('left');
        app.state.panel.position = 'right'; // set state
    },
    setContent: function(content) {
        app.panel.show();
        app.state.panel.content = content;
        app.panel.getPanelContentElement.innerHTML = content;
    },
    toggleSize: function() {
        var appPanel = app.panel.getElement;
        if (appPanel.classList.contains('expanded')) {
            appPanel.classList.remove('expanded');
        } else {
            appPanel.classList.add('expanded');
        }
    },
    form: {
        init: function() {
            app.panel.moveRight();
            app.map.layer.planningUnits.init();
            app.map.layer.scenarios.init();
            app.viewModel.scenarios.createNewScenario('/features/treatmentscenario/form/');
            initFiltering();
        },
    },
    results: {
        init: function(id) {
            app.panel.moveLeft();
            if (app.state.nav !== 'short') {
                app.state.navHeight = 'short';
                app.state.step = 'results';
            }
            if (!id) {
                id = app.viewModel.scenarios.scenarioList()[0].uid;
            }
            app.request.get_results(id)
                .then(function(response) {
                    app.panel.results.responseResultById(response);
                })
                .catch(function(response) {
                    console.log('%c failed to get results: %o', 'style: salmon;', response);
                });
        },
        responseResultById: function(result) {
            app.panel.results.aggPanel(result);
            app.panel.results.hydroPanel(result);
            app.panel.results.expander();
            app.panel.results.showAggregate();
            app.nav.showResultsNav();
        },
        addResults: function(content) {
            app.state.panel.content = content;
            app.panel.results.getPanelResultsElement.innerHTML += content;
        },
        showAggregate: function() {
            $('.result-section').removeClass('show');
            $('#aggregate-results').addClass('show');
        },
        showHydro: function() {
            $('.result-section').removeClass('show');
            $('#hydro-results').addClass('show');
        },
        expander: function() {
            if (!document.querySelector('#expand')) {
                app.panel.getPanelContentElement.insertAdjacentHTML('afterbegin', '<a id="expand" href="#" onclick="app.panel.toggleSize()" /><img class="align-self-middle" src="/static/ucsrb/img/icon/i_expand.svg" alt="expand" /></a>');
            }
        },
        aggPanel: function(content) {
            var html = `<section class="aggregate result-section" id="aggregate-results">`;
                html += `<div class="media align-items-center">
                            <img class="align-self-center mr-3" src="/static/ucsrb/img/icon/i_pie_chart.svg" alt="aggregate">
                            <div class="media-body">
                                <h4 class="mt-0">Aggregate</h4>
                            </div>
                         </div>`;
                html += `<div class="feature-result"><span class="lead">${content.aggregate_results.forest_types.forest_totals}</span> acres</div>`;
                html += `<div class="overflow-gradient">
                         <div class="result-list-wrap align-items-center">
                            <h5>Forest Management</h5>`;
                html += app.panel.results.styleObject(content.aggregate_results.forest_types);
                    html += '<h5>Landforms/Topography</h5>';
                html += app.panel.results.styleObject(content.aggregate_results['landforms/topography']);
                    html += '</div></div>';
                html += `<div class="download-wrap"><button class="btn btn-outline-primary">Download</button></div>`
             html += '</section>';

             app.panel.results.addResults(html);
        },
        hydroPanel: function(content) {
            var html = `<section class="hydro-results result-section" id="hydro-results">`;
            for (var pourpoint of content.pourpoints) {
                html += `<div id="pp-result-${pourpoint.id}" class="pourpoint-result-wrap">
                          <div class="media align-items-center">
                            <img class="align-self-center mr-3" src="/static/ucsrb/img/icon/i_pie_chart.svg" alt="aggregate">
                            <div class="media-body">
                                <h4 class="mt-0">${pourpoint.name}</h4>
                            </div>
                          </div>
                        </div>`;
                html += `<div class="feature-result"><span class="lead">${content.aggregate_results.forest_types.forest_totals}</span> acres</div>`;
            }
            app.panel.results.addResults(html);
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
        panelResultsElement: function() {
            return this.getPanelResultsElement;
        },
        get getPanelResultsElement() {
            return document.getElementById('results');
        }
    },
    draw: {
      finishDrawing: function() {
        app.panel.moveRight();
        var html = '<div class="panel-content">' +
                      '<p><b>Do you want to add another treatment area?</b></p>' +
                      '<button class="btn" onclick="app.panel.draw.addTreatmentArea()">Yes</button>' +
                      '<button class="btn" onclick="app.panel.draw.acceptDrawing()">No</button>' +
                      '<button class="btn" onclick="app.panel.draw.restart()">Restart</button>' +
                    '</div>';
        app.panel.setContent(html);
      },
      restart: function() {
        app.map.draw.source.clear(true);
        app.panel.hide();
      },
      addTreatmentArea: function() {
        app.map.draw.enable();
        var html = '<div class="panel-content">' +
                      '<p>Click on the map to start drawing your new treatment area.</p>' +
                      '<button class="btn" onclick="app.panel.draw.cancelDrawing()">Cancel</button>' +
                    '</div>';
        app.panel.setContent(html);
      },
      cancelDrawing: function() {
        app.map.draw.disable();
        app.panel.draw.finishDrawing();
      },
      acceptDrawing: function() {
        var html = '<div class="panel-content">' +
                      '<p><b>Do you want to harvest within this treatment area?</b></p>' +
                      '<button class="btn" onclick="app.panel.draw.saveDrawing()">Yes</button>' +
                      '<button class="btn" onclick="app.panel.draw.finishDrawing()">No</button>' +
                    '</div>';
        app.panel.setContent(html);
      },
      saveDrawing: function() {
        var drawFeatures = app.map.draw.source.getFeatures();
        totalArea = 0;
        for (var i = 0; i < drawFeatures.length; i++) {
          totalArea += ol.Sphere.getArea(drawFeatures[i].getGeometry());
        }
        if (drawingIsSmallEnough(totalArea)) {
          app.request.saveDrawing();
        } else {
          areaInAcres = totalArea/4046.86;
          alert('Your treatment area is too large (' + areaInAcres.toFixed(0) + ' acres). Please keep it below ' + app.map.draw.maxAcres.toString() + ' acres');
          app.panel.draw.acceptDrawing();
        }
      }
    },
    element: function() { // returns a function. to edit dom element don't forget to invoke: element()
        return this.getElement;
    },
    panelContentElement: function() { // returns a function. to edit dom element don't forget to invoke: panelContentElement()
        return this.getPanelContentElement;
    },
    get getElement() {
        return document.getElementById('panel');
    },
    get getPanelContentElement() {
        return document.getElementById('panel-content');
    }
}

enableDrawing = function() {
  app.map.draw.enable();
}

app.nav = {
    setState: function(height) {
        app.state.navHeight = height;
    },
    showResultsNav: function() {
        document.getElementById('results-nav').classList.remove('d-none');
        document.getElementById('process-nav').classList.add('d-none');
    },
    hideResultsNav: function() {
        document.getElementById('results-nav').classList.add('d-none');
        document.getElementById('process-nav').classList.remove('d-none');
    },
    short: function() {
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
        }, 1000);
    },
    tall: function() {
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
      reset: function() {
        app.panel.getPanelContentElement.innerHTML = '<div id="scenarios"></div><div id="scenario_form"></div><div id="results"></div>';
        app.panel.moveRight();
      },
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
        enableDrawing,
        false     //TODO: ??? enable editing?
      ],
      results: function() {

      }
    }
}

// using jQuery to get CSRF Token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

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
                return response;
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
    get_user_scenarios: function() {
        return $.ajax('/get_user_scenario_list/')
            .done(function(response) {
                console.log('%csuccessfully got user scenarios: %o', 'color: green', response);
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get scenarios: %o`, 'color: red', response);
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
    saveDrawing: function() {
      var drawFeatures = app.map.draw.source.getFeatures();
      var geojsonFormat = new ol.format.GeoJSON();
      var featureJson = geojsonFormat.writeFeatures(drawFeatures);

      return $.ajax({
        url: '/ucsrb/save_drawing',
        data: {
          drawing: featureJson,
          // TODO: Set name/description with form
          name: 'foo',
          description: null
        },
        dataType: 'json',
        method: 'POST',
        success: function(response) {
          console.log(`%csuccess: saved drawing`, 'color: green');
          vectors = (new ol.format.GeoJSON()).readFeatures(response.geojson, {
            dataProjection: 'EPSG:3857',
            featureProjection: 'EPSG:3857'
          });
          app.map.addScenario(vectors);
          app.panel.results.init();
        },
        error: function(response, status) {
          console.log(`%cfail @ save drawing: %o`, 'color: red', response);
          alert(response.responseJSON.error_msg);
          app.panel.draw.finishDrawing();
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
