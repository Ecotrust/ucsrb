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
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 3,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    }),
    'Streams':new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(1, 254, 136, 100)',
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 5,
        })
    }),
    'PourPoint': new ol.style.Style({
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
  'demo_routed_streams-12s94p': {
    id: 'ucsrbsupport.5t2cnpoc',
    id_field: 'EtID',
    name_field: 'Name',
    name: 'Streams'
  },
  'huc10_3857': {
    id: 'ucsrbsupport.HUC10_3857',
    id_field: 'HUC_10',
    name_field: 'HU_10_Name',
    name: 'HUC 10'
  },
  'huc12_3857': {
    id: 'ucsrbsupport.HUC12_3857',
    id_field: 'HUC_12',
    name_field: 'HU_12_NAME',
    name: 'HUC 12'
  },
  'Pour_points_3857-83a1zv': {
    id: 'ucsrbsupport.7cqwgmiz',
    id_field: 'OBJECTID',
    name_field: 'g_name',
    name: 'Pour Points'
  }
}

app.map.layer = {
    streams: {
      layer: new ol.layer.VectorTile({
        name: 'Streams',
        title: 'Streams',
        id: 'streams',
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers['demo_routed_streams-12s94p'].id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.Streams,
        visible: false
        // declutter: true
      })
    },
    pourpoints: {
      layer: new ol.layer.VectorTile({
        name: 'PourPoints',
        title: 'PourPoints',
        id: 'pourpoints',
        source: new ol.source.VectorTile({
          attributions: 'Ecotrust',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers['Pour_points_3857-83a1zv'].id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.PourPoint,
        visible: false
        // declutter: true
      })
    },
    huc10: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 10',
        title: 'HUC 10',
        id: 'huc10',
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc10_3857.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false
      })
    },
    huc12: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 12',
        title: 'HUC 12',
        id: 'huc12',
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc12_3857.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false
      })
    },
    scenarios: {
        counter: 0, // so layer is only added once
        layer: mapSettings.getInitFilterResultsLayer('scenarios', false),
        source: function() {
            return app.map.layer.scenarios.layer.getSource();
        },
        init: function(data) {
            if (app.map.layer.scenarios.counter < 1) {
                // app.map.addLayer(app.map.layer.scenarios.layer);
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
                // app.map.addLayer(app.map.layer.planningUnits.layer);
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


app.map.layer.scenarios.layer.set('id','scenarios');
app.map.layer.planningUnits.layer.set('id', 'planningUnits');

app.map.overlays = false
for (var i=0; i < app.map.getLayers().getArray().length; i++) {
  if (app.map.getLayers().getArray()[i].get('title') == 'Overlays') {
    app.map.overlays = app.map.getLayers().getArray()[i];
  }
}

if (app.map.overlays) {
  app.map.overlays.getLayers().push(app.map.layer.huc12.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc10.layer);
  app.map.overlays.getLayers().push(app.map.layer.streams.layer);
  app.map.overlays.getLayers().push(app.map.layer.pourpoints.layer);
  // app.map.overlays.getLayers().push(app.map.layer.planningUnits.layer);
  app.map.overlays.getLayers().push(app.map.layer.scenarios.layer);
}

app.map.layerSwitcher = new ol.control.LayerSwitcher({
  tipLabel: 'Legend'
});

app.map.addControl(app.map.layerSwitcher);

app.map.layerSwitcher.overlays = {};
overlays = $(".layer-switcher .panel .group label:contains('Overlays')").parent().children('ul').children('.layer');
overlays.each(function() {
  label = this.children[1].innerText;
  id = this.children[0].id;
  lyr_obj = Object.values(app.map.layer).filter(function( obj ) { return obj.layer.get('title') == label;})[0];
  app.map.layerSwitcher.overlays[lyr_obj.layer.get('id')] = {
    checkboxId: id,
    layer: lyr_obj.layer
  };
});

onFeatureClick = function(evt) {
  if (!app.map.popup) {
    app.map.popup = new ol.Overlay({
      element: document.getElementById('popup')
    });
    app.map.addOverlay(app.map.popup);

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
        markup += `<table>`;
        markup += `<tr><th>${layerDetails.name}</th><td>${properties[layerDetails.name_field]}</td></tr>`;
        markup += '</table>';
      }
    }, {hitTolerance: 3});
    if (markup) {
      $(element).popover({
        'placement': 'top',
        'animation': false,
        'html': true,
        'content': markup,
        'container': element
      });
      $(element).popover('show');
    }
  } else {
    var element = app.map.popup.getElement();
    $(element).popover('dispose');
    app.map.popup=false;
  }
}

// mapSettings.addPopup('pointermove', onFeatureClick);
mapSettings.addPopup('click', onFeatureClick);

app.map.toggleLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(true);
  $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', true);
}
