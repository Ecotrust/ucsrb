app.map = mapSettings.getInitMap();

app.map.getView().setCenter([-13363904.869732492, 6108467.733218842]);
app.map.getView().setZoom(7);

app.map.zoomToExtent = function zoomToExtent(extent) {
  ol.Map.prototype.getView.call(this).fit(extent, {duration: 2000});
}

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
        zIndex: 2,
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
        }),
        zIndex: 5
    }),
    'LineString': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#67b8c6',
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 8,
        }),
        zIndex: 2
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
        }),
        zIndex: 4
    }),
    'Polygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(0, 0, 0, 0)',
            // lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 0,   //Don't show!!!
            // width: 20,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'   //Don't show!!!
        }),
        zIndex: 2
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
        }),
        zIndex: 4
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
        }),
        zIndex: 4
    }),
    'Streams': function(feature, resolution) {
        var width = 2.25;
        if (resolution < 3) {
            width = 14;
        } else if (resolution < 5) {
            width = 11;
        } else if (resolution < 20) {
            width = 8;
        } else if (resolution < 40) {
            width = 5;
        } else if (resolution < 90) {
            width = 3.75;
        } else if (resolution < 130) {
            width = 3;
        }
        return new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'rgba(103, 184, 198, .75)',
                lineCap: 'round',
                lineJoin: 'round',
                width: width,
            }),
            zIndex: 3
        });
    },
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
        }),
        zIndex: 5
    }),
    'Boundary': new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: '#000',
        lineCap: 'cap',
        lineJoin: 'miter',
        width: 3
      }),
      fill: new ol.style.Fill({
        color: 'rgba(0,0,0,0)'
      }),
      zIndex: 1
    }),
    'Draw': new ol.style.Style({
      fill: new ol.style.Fill({
        color: [92,115,82,0.4]
      }),
      stroke: new ol.style.Stroke({
        color: [92,115,82,0.7],
        width: 2
      }),
      image: new ol.style.Circle({
        radius: 8,
        stroke: new ol.style.Stroke({
          color: 'rgba(0, 0, 0, 0.7)'
        }),
        fill: new ol.style.Fill({
          color: [92,115,82,0.5]
        })
      }),
      zIndex: 4
    })
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
  },
  'western_uc_bnd-3eremu':{
    id: 'ucsrbsupport.725p2eqc',
    id_field: 'BASIN_NAME',
    name_field: 'BASIN_NAME',
    name: 'Upper Columbia Boundary',
    // report_methods: [],
    map_layer_id: 'boundary'
  }
};

app.map.setBoundaryLayer = function(layer) {
  if (app.map.boundary) {
    layer.removeFilter(app.map.boundary);
  }
  feat = false; //Get feat from layer
  /*
    This would require switching the boundary layer to be a vector layer (not vector tile layer)
    Getting the feature could either be done by saving the the boundary as geojson locally, or getting
    it from MapBox. Here's an API call to get just the feature:
    https://www.mapbox.com/api-documentation/#retrieve-features-from-mapbox-editor-projects
    ~ RDH 4/20/2018
  */
  app.map.boundary = new ol.filter.Mask({feature: feat, inner: false, fill: new ol.style.Fill({color:[0,0,0,0.6]})});
  layer.addFilter(app.map.boundary);
  app.map.boundary.set('active', true);
}

app.map.removeBoundary = function() {
  app.map.boundary.set('active', false);
}

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
    if (app.state.stepVal < 1 || app.state.stepVal == 'reset') {
      app.state.step = 1;
    } else if (app.state.stepVal == 2) {
      // if already on step 2 then a new pourpoint has been selected
      // we need to the reset the filter form and then go back to step 2
      app.state.step = 'reset';
      app.state.step = 2;
    } else {
      app.state.step = 2;
    }
  } else {
    if (app.state.stepVal < 1 || app.state.stepVal == 'reset') {
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

app.map.closePopup = function() {
  if (app.map.hasOwnProperty('popup') && app.map.popup != false) {
    var element = app.map.popup.getElement();
    $(element).popover('hide');
    $(element).popover('dispose');
  }
  app.map.popup=false;
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
  // app.map.popupLock = true;
  // app.map.closePopup();
  // app.map.popup = new ol.Overlay({
    // element: document.getElementById('popup')
  // });
  // var element = app.map.popup.getElement();
  // app.map.addOverlay(app.map.popup);
  // extent = feat.getExtent();
  // coordinate = [(extent[0]+extent[2])/2, (extent[1]+extent[3])/2];
  // app.map.popup.setPosition(coordinate);
  // var unit_type = mbLayer.name;
  // var unit_name = feat.get(mbLayer.name_field);
  // var title = unit_type + ': ' + unit_name + '&nbsp<button class="btn btn-danger" type="button" onclick="closeConfirmSelection(false);">&times;</button>';

  // $(element).popover({
  //   'placement': 'top',
  //   'animation': false,
  //   'html': true,
  //   'content': markup,
  //   'container': element,
  //   'title': title
  // });
  // $(element).popover('show');
}

closeConfirmSelection = function(accepted) {
  app.map.closePopup();
  if (!accepted) {
    app.map.popupLock = false;
    removeFilter();
  }
  app.map.selection.select.getFeatures().clear();
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
      confirmationReceived();
    }
  });
};

streamSelectAction = function(feat) {
  if (app.scenarioInProgress()) {
    app.map.mask.set('active', false);
    app.viewModel.scenarios.reset({cancel: true});
    app.state.step = 0; // go back to step one
  }
  app.map.enableLayer('pourpoints');
  app.map.zoomToExtent(feat.getExtent());
  if (app.state.stepVal < 1) {
    app.state.step = 1; // step forward in state
  }
};

pourPointSelectAction = function(feat, selectEvent) {
  app.request.get_basin(feat, function(feat, vector) {
    if (feat) {
      markup = generateFilterPopup('<p>Find harvest locations within this basin?</p>');
      confirmSelection(feat, markup, vector);
    }
    if (app.state.stepVal < 2) {
      app.state.step = 2; // step forward in state
    }
  });
};

var drawSource = new ol.source.Vector();
var drawInteraction = new ol.interaction.Draw({
  source: drawSource,
  type: "Polygon",
});
var snapInteraction = new ol.interaction.Snap({source: drawSource});
var modifyInteraction = new ol.interaction.Modify({source: drawSource});

app.map.draw = {
  maxAcres: 5000,
  source: drawSource,
  draw: drawInteraction,
  snap: snapInteraction,
  modify: modifyInteraction,
  enable: function() {
    app.map.addInteraction(drawInteraction);
    app.map.addInteraction(snapInteraction);
    createMeasureTooltip();
    map.on('pointermove', pointerMoveHandler);
  },
  enableEdit: function() {
    // app.map.removeInteraction(drawInteraction);
    app.map.addInteraction(modifyInteraction);
    // app.map.addInteraction(snapInteraction);
  },
  // disableEdit: function() {
  //   app.map.removeInteraction(modifyInteraction);
  //   app.map.removeInteraction(snapInteraction);
  // },
  disable: function() {
    app.map.removeInteraction(modifyInteraction);
    app.map.removeInteraction(drawInteraction);
    app.map.removeInteraction(snapInteraction);
    map.on('pointermove', pointerMoveHandler);
  },
  getDrawingArea: function() {
    var drawFeatures = app.map.draw.source.getFeatures();
    totalArea = 0;
    for (var i = 0; i < drawFeatures.length; i++) {
        totalArea += ol.Sphere.getArea(drawFeatures[i].getGeometry());
    }
    return totalArea;
  },
};

app.map.draw.draw.on('drawstart', function(e) {
  if (app.state.stepVal == 0) {
    app.state.step = 1;
  }

  /** @type {ol.Coordinate|undefined} */
  var tooltipCoord = e.coordinate;

  app.map.draw.toolTipListener = e.feature.getGeometry().on('change', function(evt) {
    var geom = evt.target;
    var output = formatAreaToAcres(geom);
    var tooltipCoord = geom.getInteriorPoint().getCoordinates();
    app.map.draw.measureTooltipElement.innerHTML = output;
    app.map.draw.measureTooltip.setPosition(tooltipCoord);
  });
});

app.map.draw.draw.on('drawend', function(e) {
  app.map.draw.enableEdit();
  app.panel.draw.finishDrawing();
});

app.map.draw.measureTooltipElement;
app.map.draw.measureTooltip;
app.map.draw.toolTipListener;

app.map.draw.modify.on('modifyend', function(e) {
  console.log('change');
  app.panel.draw.finishDrawing();
});

/**
 * Handle pointer move for drawing
 * @param {ol.MapBrowserEvent} evt The event.
 */
var pointerMoveHandler = function(evt) {
  if (evt.dragging) {
    return;
  }
  var drawFeatures = app.map.draw.source.getFeatures();
  if (drawFeatures.length > 0) {
    var geom = (drawFeatures[0].getGeometry());
  }
};

/**
 * Format area output.
 * @param {ol.geom.Polygon} polygon The polygon.
 * @return {string} Formatted area.
 */
var formatAreaToAcres = function(polygon) {
  var area = ol.Sphere.getArea(polygon);
  var output = Math.round(area * 0.00024710538146717) + ' ' + 'acres';
  return output;
};

/**
 * Creates a new measure tooltip
 */
function createMeasureTooltip() {
  if (app.map.draw.measureTooltipElement) {
    app.map.draw.measureTooltipElement.parentNode.removeChild(app.map.draw.measureTooltipElement);
  }
  app.map.draw.measureTooltipElement = document.createElement('div');
  app.map.draw.measureTooltipElement.className = 'tooltip tooltip-measure';
  app.map.draw.measureTooltip = new ol.Overlay({
    element: app.map.draw.measureTooltipElement,
    offset: [0, -15],
    positioning: 'bottom-center'
  });
  app.map.addOverlay(app.map.draw.measureTooltip);
}

app.map.layer = {
    draw: {
      layer: new ol.layer.Vector({
        source: app.map.draw.source,
        style: app.map.styles.Draw
      })
    },
    boundary: {
      layer: new ol.layer.VectorTile({
        name: 'Upper Columbia Boundary',
        title: 'Upper Columbia Boundary',
        id: 'boundary',
        source: new ol.source.VectorTile({
          attributions: 'Ecotrust',
          format: new ol.format.MVT(),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers['western_uc_bnd-3eremu'].id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.Boundary,
        visible: false,
      })
    },
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
        layer: mapSettings.getInitFilterResultsLayer('scenarios', false),
        source: function() {
            return app.map.layer.scenarios.layer.getSource();
        }
    },
    planningUnits: {
        layer: mapSettings.getInitFilterResultsLayer('planning units', app.map.styles['Polygon']),
        source: function() {
            return app.map.layer.planningUnits.layer.getSource();
        },
        addFeatures: function(features) {
            features.forEach(function(el,i,arr) {
                app.map.layer.planningUnits.layer.addWKTFeatures(el);
            });
        },
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
  app.map.overlays.getLayers().push(app.map.layer.draw.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc12.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc10.layer);
  app.map.overlays.getLayers().push(app.map.layer.streams.layer);
  app.map.overlays.getLayers().push(app.map.layer.pourpoints.layer);
  app.map.overlays.getLayers().push(app.map.layer.boundary.layer);
}

app.map.layerSwitcher = new ol.control.LayerSwitcher({
  tipLabel: 'Layers'
});

app.map.addControl(app.map.layerSwitcher);

app.map.toggleMapControls = function(show) {
    if (show) {
        $('.ol-control').removeClass('hide');
    } else {
        $('.ol-control').addClass('hide');
    }
}

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

app.map.forestFilterOverlays = {}


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

app.map.addScenario = function(vectors) {
  app.map.draw.source.clear(true);
  app.map.draw.source.addFeatures(vectors);
};

app.map.dropPin = function(coords) {
  if (app.map.dropPin.source) {
    app.map.dropPin.source.clear();
  } else {
    app.map.dropPin.source = new ol.source.Vector();
    app.map.dropPin.layer = new ol.layer.Vector({
      source: app.map.dropPin.source
    });
    app.map.addLayer(app.map.dropPin.layer);
  }
  app.map.dropPin.pin = new ol.Feature({
    geometry: new ol.geom.Point(coords)
  });
  app.map.dropPin.pin.setStyle(app.map.styles.Point);
  app.map.dropPin.source.addFeature(app.map.dropPin.pin);
}
