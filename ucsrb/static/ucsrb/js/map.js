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
    'Draw': new ol.style.Style({
      fill: new ol.style.Fill({
        color: 'rgba(255, 255, 255, 0.4)'
      }),
      stroke: new ol.style.Stroke({
        // color: '#ffcc33',
        color: 'rgba(215, 160, 11, 1)',
        width: 4
      }),
      image: new ol.style.Circle({
        radius: 7,
        fill: new ol.style.Fill({
          color: 'rgba(255, 204, 51, 1)'
        })
      })
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
    if (app.state.stepVal < 2 || app.state.stepVal == 'reset') {
      app.state.step = 2; // step forward in state
    } else if (app.state.stepVal == 2) {
      // if already on step 2 then a new pourpoint has been selected
      // we need to the reset the filter form and then go back to step 2
      app.state.step = 'reset';
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
  if (app.map.hasOwnProperty('popup')) {
    var element = app.map.popup.getElement();
    $(element).popover('dispose');
  }
  app.map.popup = new ol.Overlay({
    element: document.getElementById('popup')
  });
  var element = app.map.popup.getElement();
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
  },
  enableEdit: function() {
    app.map.removeInteraction(drawInteraction);
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
  }
};

app.map.draw.draw.on('drawstart', function(e) {
  if (app.state.stepVal == 0) {
    app.state.step = 1;
  }
});

app.map.draw.draw.on('drawend', function(e) {
  app.map.draw.enableEdit();
  app.panel.draw.finishDrawing();
});

app.map.layer = {
    draw: {
      layer: new ol.layer.Vector({
        source: app.map.draw.source,
        style: app.map.styles.Draw
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

app.map.addScenario = function(vectors) {
  app.map.draw.source.clear(true);
  app.map.draw.source.addFeatures(vectors);
};

/**
  * @constructor
  * @extends {ol.control.Control}
  * @param {Object=} opt_options Control options.
  */
app.geoSearch = function(opt_options) {
    var options = opt_options || {};

    var button = document.createElement('button');

    var input = document.createElement('input');
    input.className = 'ol-geo-search-input form-control d-none'
    input.setAttribute('id', 'geo-search-input');
    input.setAttribute('placeholder', 'Search ...');
    input.setAttribute('type', 'search');

    var resultsList = document.createElement('ul');
    resultsList.setAttribute('id', 'autocomplete-results')

    var this_ = this;
    var viewResult = function(center,zoom) {
        this_.getMap().getView().setCenter(center);
        this_.getMap().getView().setZoom(zoom);
    };
    var toggleSearchBox = function() {
        var input = document.querySelector('#geo-search-input');
        var resultsList = document.getElementById("autocomplete-results");
        if (input.classList.contains('d-none')) {
            input.classList.remove('d-none');
            app.geoSearch.autoCompleteLookup();
        } else {
            input.value = '';
            input.classList.add('d-none');
        }
    };

    button.addEventListener('click', toggleSearchBox, false);

    var element = document.createElement('div');
    element.className = 'ol-geo-search ol-unselectable ol-control geo-search form-inline';
    element.appendChild(button);
    element.appendChild(input);
    element.appendChild(resultsList);

    ol.control.Control.call(this, {
        element: element,
        target: options.target
    });
};

app.geoSearch.geojson = function(callback) {
    return function(callback) {
        $.ajax("/static/ucsrb/data/gnis_3857.geojson", callback);
    }
}

app.geoSearch.autoCompleteLookup = function() {
    var input = document.querySelector('#geo-search-input');
    var resultsList = document.getElementById("autocomplete-results");
    input.onkeyup = function(e) {
        var input_val = this.value;
        if (input_val.length > 2) {
            resultsList.innerHTML = '';
            options = app.geoSearch.autoCompleteResults(input_val);

            for (var option in options) {
                resultsList.innerHTML += `<li>${option}</li>`;
            }
            resultsList.style.display = 'block';
        } else {
            resultsList.innerHTML = '';
        }
    }
}

app.geoSearch.autoCompleteResults = function(val) {
    var options = [];
    var geojson = app.geoSearch.geojson(function(response) {
        console.log('%csuccessfully return geosearch json', 'color: green');
        var json = JSON.parse(response);
        return json;
    });
    for (var feature in geojson.features) {
        if (val === feature['properties']['F_NAME'].slice(0, val.length)) {
            options.push(feature['properties']['F_NAME']);
        }
    }
    return options;
}

ol.inherits(app.geoSearch, ol.control.Control);
var geoSearchControl = new app.geoSearch();
app.map.addControl(geoSearchControl);
