app.map = mapSettings.getInitMap();

app.map.styles = {
    'Point': new ol.style.Style({
        image: new ol.style.Circle({
            radius: 8,
            fill:  new ol.style.Fill({
                color: '#67b8c6',
            }),
            stroke: new ol.style.Stroke({
                color: '#ffffff',
                width: 2,
            }),
        }),
        zIndex: 1,
    }),
    'PointSelected': new ol.style.Style({
        image: new ol.style.Circle({
            radius: 16,
            fill:  new ol.style.Fill({
                color: '#4D4D4D',
            }),
            stroke: new ol.style.Stroke({
                color: '#ffffff',
                width: 3,
            }),
        })
    }),
    'LineString': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#67b8c6',
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 8,
        })
    }),
    'LineStringSelected': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#3a5675',
            width: 6,
        }),
        image: new ol.style.Circle({
            radius: 10,
            fill:  new ol.style.Fill({
                color: '#FCC'
            }),
            stroke: new ol.style.Stroke({
                color: '#3a5675',
                width: 5,
            }),
        })
    }),
    'Polygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(93, 116, 82, 0.9)',
            // lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 0,   //Don't show!!!
            // width: 20,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'   //Don't show!!!
        })
    }),
    'PolygonSelected': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#58595b',
            lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 1,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(93, 116, 82, 0.45)'
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

/**
* Map - Layers, Sources, Features
*/

app.mapbox.layers = {
  'demo_routed_streams-12s94p': {
    id: 'ucsrbsupport.5t2cnpoc',
    id_field: 'EtID',
    name_field: 'Name',
    name: 'Streams',
    report_methods: ['select'],
    map_layer_id: 'streams'
  },
  'huc10_3857': {
    id: 'ucsrbsupport.HUC10_3857',
    id_field: 'HUC_10',
    name_field: 'HU_10_Name',
    name: 'HUC 10',
    report_methods: ['filter'],
    map_layer_id: 'huc10'
  },
  'huc12_3857': {
    id: 'ucsrbsupport.HUC12_3857',
    id_field: 'HUC_12',
    name_field: 'HU_12_NAME',
    name: 'HUC 12',
    report_methods: ['filter'],
    map_layer_id: 'huc12'
  },
  'Pour_points_3857-83a1zv': {
    id: 'ucsrbsupport.7cqwgmiz',
    id_field: 'OBJECTID',
    name_field: 'g_name',
    name: 'Pour Points',
    report_methods: ['select'],
    map_layer_id: 'pourpoints'
  }
};

setFilter = function(feat, layer) {
  if (app.map.mask) {
    layer.removeFilter(app.map.mask);
  }
  app.map.mask = new ol.filter.Mask({feature: feat, inner: false, fill: new ol.style.Fill({color:[0,0,0,0.6]})});
  layer.addFilter(app.map.mask);
  app.map.mask.set('active', true);
  app.map.zoomToExtent(feat.getGeometry().getExtent());
}

removeFilter = function() {
  app.map.mask.set('active', false);
}

confirmationReceived = function() {
  if (app.state.method == 'select') {
    if (app.state.stepVal < 2) {
      app.state.step = 2; // step forward in state
    } else if (app.state.stepVal == 2) {
      // if already on step 2 then a new pourpoint has been selected
      // we need to the reset the filter form and then go back to step 2
      app.state.step = 'reset';
      app.state.step = 2;
    }
  } else {
    if (app.state.stepVal < 1) {
      app.state.step = 1; // step forward in state
    } else if (app.state.stepVal == 1) {
      // if already on step 2 then a new forest unit has been selected
      // we need to the reset the filter form and then go back to step 1
      app.state.step = 'reset';
      app.state.step = 1;
    }
  }
  closeConfirmSelection(true);
}

confirmSelection = function(feat, markup, vector) {
  mbLayer = app.mapbox.layers[feat.getProperties().layer];
  layer = app.map.layer[mbLayer.map_layer_id];
  features = (new ol.format.GeoJSON()).readFeatures(vector, {
    dataProjection: 'EPSG:3857',
    featureProjection: 'EPSG:3857'
  });
  if (app.state.method == 'select') {
    // hack for when we have no ppt basins and default to HUC 12.
    setFilter(features[0], app.map.layer.pourpoints.layer);
  } else {
    setFilter(features[0], layer.layer);
  }
  app.map.popupLock = true;
  var element = app.map.popup.getElement();
  $(element).popover('dispose');
  app.map.popup = new ol.Overlay({
    element: document.getElementById('popup')
  });
  app.map.addOverlay(app.map.popup);
  extent = feat.getExtent();
  coordinate = [(extent[0]+extent[2])/2, (extent[1]+extent[3])/2];
  app.map.popup.setPosition(coordinate);
  var unit_type = mbLayer.name;
  var unit_name = feat.get(mbLayer.name_field);
  var title = unit_type + ': ' + unit_name + '&nbsp<button class="btn btn-danger" type="button" onclick="closeConfirmSelection(false);">&times;</button>';

  $(element).popover({
    'placement': 'top',
    'animation': false,
    'html': true,
    'content': markup,
    'container': element,
    'title': title
  });
  $(element).popover('show');
}

closeConfirmSelection = function(accepted) {
  var element = app.map.popup.getElement();
  $(element).popover('hide');
  $(element).popover('dispose');
  if (!accepted) {
    app.map.popupLock = false;
    removeFilter();
  }
}

generateFilterPopup = function(content) {
   // return '<button class="btn btn-danger" type="button" onclick="closeConfirmSelection();">&times;</button>' +
   return '' +
    content + '<div class="popover-bottom-confirm-buttons">' +
    '<button class="btn btn-success" type="button" onclick="confirmationReceived()">Yes</button>' +
    '<button class="btn btn-danger" type="button" onclick="closeConfirmSelection(false);">No</button>' +
    '</div>';
}

focusAreaSelectAction = function(feat) {
  var layer = app.map.selection.select.getLayer(feat).get('id');
  app.request.get_focus_area(feat, layer, function(feat, vector) {
    if (feat){
      markup = generateFilterPopup('<p>Find harvest locations within this watershed?</p>');
      confirmSelection(feat, markup, vector);
    }
  });
};

streamSelectAction = function(feat) {
  app.map.enableLayer('pourpoints');
  app.map.zoomToExtent(feat.getExtent());
  if (app.state.stepVal < 1) {
    app.state.step = 1; // step forward in state
  }
};

pourPointSelectAction = function(feat) {
  app.request.get_basin(feat, function(feat, vector) {
    if (feat){
      markup = generateFilterPopup('<p>Find harvest locations within this basin?</p>');
      confirmSelection(feat, markup, vector);
    }
  });
};

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
        visible: false,
        renderBuffer: 500,
        // declutter: true
      }),
      selectAction: streamSelectAction
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
        visible: false,
        renderBuffer: 500
        // declutter: true
      }),
      selectAction: pourPointSelectAction
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
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
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
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
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
                // TODO stop this from blocking fitering
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
        layer: mapSettings.getInitFilterResultsLayer('planning units', app.map.styles['Polygon']),
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
                app.map.layer.planningUnits.counter++;
                console.log('%cplanning unit layer added', 'color: green');
            } else {
                console.log('%cplanning unit layer already added', 'color: orange');
            }
        }
    },
};

app.map.layer.scenarios.layer.set('id','scenarios');
app.map.layer.planningUnits.layer.set('id', 'planningUnits');

app.map.overlays = false;
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
  tipLabel: 'Layers'
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

app.map.enableLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(true);
  $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', true);
};

app.map.disableLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(false);
  if (app.map.layerSwitcher.overlays[layerName]) {
    $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', false);
  }
};

app.map.toggleLayer = function(layerName) {
  if ($('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked')){
    app.map.disableLayer(layerName);
  } else {
    app.map.enableLayer(layerName);
  }
};

app.map.clearLayers = function() {
  var layerNames = Object.keys(app.map.layer);
  for (var i = 0; i < layerNames.length; i++) {
    app.map.disableLayer(layerNames[i]);
  }
}
