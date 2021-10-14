/**
* Pointer Interactions
*/

isFeatureRelevant = function(feature) {
  // return (layersClicked.indexOf(layerName) < 0 && app.mapbox.layers[layerName].report_methods.indexOf(app.state.method) >= 0) {
  try {
    return app.mapbox.layers[feature.getProperties().layer].report_methods.indexOf(app.state.method) >= 0;
  } catch (err) {
    return false;
  }
}

// Mostly ripped from http://openlayers.org/en/master/examples/custom-interactions.html
/**
 * @constructor
 * @extends {ol.interaction.Pointer}
 */
app.map.PointerType = function() {

  ol.interaction.Pointer.call(this, {
    handleMoveEvent: app.map.PointerType.prototype.handleMoveEvent,
    handleUpEvent: app.map.PointerType.prototype.handleUpEvent
  });

  /**
   * @type {ol.Pixel}
   * @private
   */
  this.coordinate_ = null;

  /**
   * @type {string|undefined}
   * @private
   */
  this.cursor_ = 'pointer';

  /**
   * @type {ol.Feature}
   * @private
   */
  this.feature_ = null;

  /**
   * @type {string|undefined}
   * @private
   */
  this.previousCursor_ = undefined;

};
ol.inherits(app.map.PointerType, ol.interaction.Pointer);

/**
* Popup Logic
*/
app.map.popupLock = false;

/**
* @param {ol.MapBrowserEvent} evt Event.
*/
app.map.PointerType.prototype.handleMoveEvent = function(evt) {
  if (app.map.popup && !app.map.popupLock) {
    app.map.closePopup();
    app.map.popup=false;
  }
  if (this.cursor_) {
    var map = evt.map;
    let markup = '';
    layersClicked = [];
    feature = null;

    map.forEachFeatureAtPixel(evt.pixel,
      function(feat) {
        feature = feat;
        if (isFeatureRelevant(feat)) {
          const properties = feat.getProperties();
          var layerName = properties.layer;
          layersClicked.push(layerName);
          var layerDetails = app.mapbox.layers[layerName];
          markup += `<table>`;
          markup += `<tr><th>${layerDetails.name}</th><td>${properties[layerDetails.name_field]}</td></tr>`;
          markup += '</table>';
        }
      }
    );

    if (markup && !app.map.popupLock) {
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

      $(element).popover({
        'placement': 'top',
        'animation': false,
        'html': true,
        'content': markup,
        'container': element
      });
      $(element).popover('show');
    }

    var element = evt.map.getTargetElement();
    if (feature && isFeatureRelevant(feature)) {
      if (element.style.cursor != this.cursor_) {
        this.previousCursor_ = element.style.cursor;
        element.style.cursor = this.cursor_;
      }
    } else if (this.previousCursor_ !== undefined) {
      element.style.cursor = this.previousCursor_;
      this.previousCursor_ = undefined;
    }
  }
};


/**
 * @return {boolean} `false` to stop the drag sequence.
 */
app.map.PointerType.prototype.handleUpEvent = function() {
  this.coordinate_ = null;
  this.feature_ = null;
  return false;
};

app.map.Pointer = new app.map.PointerType;

app.map.selection = {};
// Via http://openlayers.org/en/master/examples/select-features.html?q=select
app.map.selection.select = null;  // ref to currently selected interaction
// select interaction working on "singleclick"
app.map.selection.selectNoneSingleClick = new ol.interaction.Select(
  {
    layers: []
  }
);
app.map.selection.selectSelectSingleClick = new ol.interaction.Select(
  {
    layers: [
      app.map.layer.streams.layer,
      app.map.layer.pourpoints.layer,
    ],
    style: app.map.styles.LineStringSelected
  }
);
app.map.selection.selectFilterSingleClick = new ol.interaction.Select(
  {
    layers: [
      app.map.layer.huc10.layer,
      app.map.layer.huc12.layer,
      app.map.layer.RMU.layer,
    ],
    style: app.map.styles.Polygon
  }
);
// app.map.selection.selectResultsPourPoint = new ol.interaction.Select(
app.map.selection.selectResultsFeature = new ol.interaction.Select(
  {
    layers: [
      app.map.layer.resultPoints.layer,
      app.map.layer.treatmentResultAreas.layer,
    ],
    // style: app.map.styles.PourPointSelected
    // style: app.map.styles.SelectedReportFeature
  }
);

// For selection of drawings to apply prescriptions
app.map.selection.selectTreatmentArea = new ol.interaction.Select(
  {
    layers: [
      app.map.layer.treatmentAreas.layer
    ],
    style: app.map.styles.SelectedTreatmentArea,
    condition: function(e) {
      setTimeout(function() {
        // make sure count gets updated when things are all unselected, too
        app.prescription.updateTreatmentSectionCount();
      }, 20);
      return (e.type == 'click');
    },
    toggleCondition: function(e) {
      // Toggle selection on clicks to features only
      return (e.type == 'click');
    },

  }
);

app.map.selection.clearSelects = function() {
  if (app.map.selection.select) {
    for (var i = 0; i < app.map.selection.select.length; i++) {
      app.map.removeInteraction(app.map.selection.select[i]);
    }
  }
  app.map.selection.select = [];
}

app.map.selection.addSelect = function(selectionInteraction) {
  app.map.selection.select.push(selectionInteraction);
  app.map.addInteraction(selectionInteraction);
  selectionInteraction.on('select', function(event) {
    var selected_features = selectionInteraction.getFeatures().getArray();
    if (selected_features.length > 0) {
      selectionInteraction.getFeatures().forEach(function(feat) {
        var layer = selectionInteraction.getLayer(feat).get('id');
        app.map.layer[layer].selectAction(feat, event);
      });
    } else {
      event.preventDefault();
    }
  });
}

app.map.selection.setSelect = function(selectionInteractions) {
  app.map.selection.clearSelects();
  if (selectionInteractions.length == undefined) {
    selectionInteractions = [selectionInteractions]
  }
  for (var i = 0; i < selectionInteractions.length; i++) {
    var selectionInteraction = selectionInteractions[i];
    app.map.selection.select.push(selectionInteraction);
    app.map.addInteraction(selectionInteraction);
    app.map.selection.select[i].on('select', function(event) {
      event.target.getFeatures().forEach(function(feat) {
          var layer = event.target.getLayer(feat).get('id');
          app.map.layer[layer].selectAction(feat, event);
      });
    });
  }
};
