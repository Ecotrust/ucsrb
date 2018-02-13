app.map = mapSettings.getInitMap();

app.map.styles = {
    'Point': new ol.style.Style({
        image: new ol.style.Circle({
            radius: 10,
            fill:  new ol.style.Fill({
                color: '#ffffff'
            }),
            stroke: new ol.style.Stroke({
                color: '#aaffff',
                width: 5,
            }),
        })
    }),
    'LineString': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#67b8c6',
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 4,
        })
    }),
    'LineStringSelected': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#3a5675',
            width: 6,
        })
    }),
    'Polygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#58595b',
            lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 3,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    }),
    'PolygonSelected': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#58595b',
            lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 3,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 255, 0.1)'
        })
    }),
    'FocusArea': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#58595b',
            // lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 3,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    })
};

app.map.interaction = {
    select: {
        segment: function() {
            var select = new ol.interaction.Select({
                style: app.map.styles['LineStringSelected'],
                layers: [app.map.layer.streams.layer],
                hitTolerance: 1
            });
            app.map.addInteraction(select);
            select.on('select', function(event) {
                app.map.layer.streams.segment.init(event);
            });
        },
        pourpoint: function() {
            var select = new ol.interaction.Select({
                style: app.map.styles['Point'],
                layers: [app.map.layer.pourpoints.layer],
                hitTolerance: 1,
            });
            app.map.addInteraction(select);
            return select.on('select', function(event) {
                var collection = event.target.getFeatures();
                collection.forEach(function(el,i,arr) {
                    var props = el.getProperties();
                    console.log('%c selected: %o', 'color: #05b8c3', arr);
                    app.request.get_basin(props.properties.id)
                        .then(function(data) {
                            app.request.saveState(); // save state prior to filter
                        });
                });
                app.panel.form.init();
                app.state.step = 2;
            });
        },
    },
    get selection() {
        return this.select;
    }
}



/**
* Map - Layers, Sources, Features
*/

app.mapbox.layers = {
  'huc10_3857': {
    id: 'ucsrbsupport.HUC10_3857',
    id_field: 'HUC_10',
    name_field: 'HU_10_Name',
    name: 'HUC 10'
  },
  'huc12_3857': {
    id: 'ucsrbsupport.HUC12_3857',
    id_field: 'HUC_12',
    name_field: 'HU_12_Name',
    name: 'HUC 12'
  }
}

app.map.layer = {
    streams: {
        data: {}, // store init data
        counter: 0, // so layer is only added once
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        }),
        layer: new ol.layer.Vector({
            style: app.map.styles['LineString']
        }),
        feature: function(data) {
            return new ol.Feature({
                geometry: new ol.geom.LineString(data.geometry.geometry.coordinates),
                name: data.name,
                properties: {
                    id: data.id,
                    pourpoints: data.pourpoints
                }
            });
        },
        init: function(data) {
            // Check if layer has already been added
            if (app.map.layer.streams.counter === 0) {
                app.map.layer.streams.data = data;
                var feature = app.map.layer.streams.feature(data);
                app.map.layer.streams.source.addFeature(feature);
                app.map.layer.streams.layer.setSource(app.map.layer.streams.source);
                app.map.addLayer(app.map.layer.streams.layer);
                app.map.layer.streams.counter++;
            } else {
                console.log('%cstreams already added', 'color: orange;');
            }
        },
        segment: {
            data: {}, // store init data
            init: function(data) {
                if (data.selected.length > 0) {
                    var selected = data.selected[0].getProperties();
                    app.map.layer.streams.segment.data = selected;
                    app.map.layer.pourpoints.data = selected.properties.pourpoints;
                    app.map.layer.pourpoints.init();
                    app.map.interaction.select.pourpoint();
                }
            },
        },
    },
    pourpoints: {
        data: {}, // store init data
        counter: 0, // so layer is only added once
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        }),
        layer: new ol.layer.Vector({
            style: function(feature) {
                return app.map.styles['Point'];
            },
            zIndex: 1,
        }),
        init: function() {
            // Check if layer has already been added
            if (app.map.layer.pourpoints.counter === 0) {
                app.map.layer.pourpoints.data.forEach(function(pp,i,a) {
                    var feature = new ol.Feature({
                        geometry: new ol.geom.Point(pp.geometry.geometry.coordinates),
                        name: pp.name,
                        properties: {
                            id: pp.id
                        }
                    });
                    app.map.layer.pourpoints.source.addFeature(feature);
                });
                app.map.layer.pourpoints.layer.setSource(app.map.layer.pourpoints.source);
                app.map.addLayer(app.map.layer.pourpoints.layer);
                app.map.layer.pourpoints.counter++;
                app.state.step = 1; // step forward in state
            } else {
                console.log('%cstreams already added', 'color: orange');
            }
        }
    },
    huc10: new ol.layer.VectorTile({
        name: 'HUC 10',
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc10_3857.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea
    }),
    huc12: new ol.layer.VectorTile({
        name: 'HUC 12',
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc12_3857.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea
    }),
    scenarios: {
        counter: 0, // so layer is only added once
        layer: mapSettings.getInitFilterResultsLayer('scenarios', false),
        source: function() {
            return app.map.layer.scenarios.layer.getSource();
        },
        init: function(data) {
            if (app.map.layer.scenarios.counter < 1) {
                app.map.addLayer(app.map.layer.scenarios.layer);
                app.request.get_scenarios()
                    .then(function(response) {
                        var html = `<div class="dropdown">
                                        <button class="btn btn-secondary dropdown-toggle" type="button" id="savedScenarioDropdownBtn" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select Saved Treatment</button>
                                        <div class="dropdown-menu" aria-labelledby="savedScenarioDropdownBtn">`;
                        response.forEach(function(scenario,i,arr) {
                            var scenario_name = scenario.name;
                            if (scenario.name == '') {
                                scenario_name = `Scenario ${scenario.id}`;
                            }
                            var scenario_link = `/features/treatmentscenario/ucsrb_treatmentscenario/${scenario.id}`;
                            html += `<a class="dropdown-item" href="${scenario_link}/">${scenario_name}</a>`;
                        });
                        html += "</div>"
                        $('#scenarios').html(html);
                    });
                app.map.layer.scenarios.counter++;
            } else {
                console.log('%cscenarios layer already added', 'color: orange');
            }
        }
    },
    planningUnits: {
        counter: 0,
        layer: mapSettings.getInitFilterResultsLayer('planning units', app.map.styles['PolygonSelected']),
        source: function() {
            return app.map.layer.planningUnits.layer.getSource();
        },
        addFeatures: function(features) {
            features.forEach(function(el,i,arr) {
                app.map.layer.planningUnits.layer.addWKTFeatures(el);
            });
        },
        init: function() {
            if (app.map.layer.planningUnits.counter < 1) {
                app.map.addLayer(app.map.layer.planningUnits.layer);
                app.request.get_planningunits()
                    .then(function(response) {
                        app.map.layer.planningUnits.addFeatures(response);
                    });
                app.map.layer.planningUnits.counter++;
            } else {
                console.log('%cplanning unit layer already added', 'color: orange');
            }
        }
    },
}

// Despite the name, this is being used for pointermove/hover
onFeatureClick = function(evt) {
  if (!app.map.popup) {
    app.map.popup = new ol.Overlay({
      element: document.getElementById('popup')
    });
    app.map.addOverlay(app.map.popup);
  }

  var element = app.map.popup.getElement();
  var coordinate = evt.coordinate;
  var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(
    coordinate, 'EPSG:3857', 'EPSG:4326'
  ));
  $(element).popover('dispose');
  app.map.popup.setPosition(coordinate);
  let markup = '';
  featureCount = 0;
  layersClicked = [];
  map.forEachFeatureAtPixel(evt.pixel, function(feature) {
    featureCount += 1;
    console.log('feature: ' + featureCount);
    const properties = feature.getProperties();
    var layerName = properties.layer;
    if (layersClicked.indexOf(layerName) < 0) {
      layersClicked.push(layerName);
      var layerDetails = app.mapbox.layers[layerName];
      markup += `${markup}<table>`;
      markup += `<tr><th>${layerDetails.name}</th><td>${properties[layerDetails.name_field]}</td></tr>`;
      markup += '</table>';
    }
  }, {hitTolerance: 1});
  if (markup) {
    $(element).popover({
      'placement': 'top',
      'animation': false,
      'html': true,
      'content': markup
    });
    $(element).popover('show');
  }
}

app.map.popup = mapSettings.addPopup('pointermove', onFeatureClick);
