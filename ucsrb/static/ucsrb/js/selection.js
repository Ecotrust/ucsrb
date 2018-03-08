/**
* Pointer Interactions
*/

isFeatureRelevant = function(feature) {
  // return (layersClicked.indexOf(layerName) < 0 && app.mapbox.layers[layerName].report_methods.indexOf(app.state.method) >= 0) {
  return app.mapbox.layers[feature.getProperties().layer].report_methods.indexOf(app.state.method) >= 0;
}

// Mostly ripped from http://openlayers.org/en/master/examples/custom-interactions.html
/**
 * @constructor
 * @extends {ol.interaction.Pointer}
 */
app.map.Pointer = function() {

  ol.interaction.Pointer.call(this, {
    handleMoveEvent: app.map.Pointer.prototype.handleMoveEvent,
    handleUpEvent: app.map.Pointer.prototype.handleUpEvent
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
ol.inherits(app.map.Pointer, ol.interaction.Pointer);

/**
* @param {ol.MapBrowserEvent} evt Event.
*/
app.map.Pointer.prototype.handleMoveEvent = function(evt) {
  if (app.map.popup) {
    var element = app.map.popup.getElement();
    $(element).popover('dispose');
    app.map.popup=false;
  }
  if (this.cursor_) {
    var map = evt.map;
    let markup = '';
    layersClicked = [];
    feature = null;
    app.map.selection.select.getFeatures().forEach(function(feat) {

    });

    map.forEachFeatureAtPixel(evt.pixel,
      function(feat) {
        feature = feat;
        if (isFeatureRelevant) {
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

    if (markup) {
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
app.map.Pointer.prototype.handleUpEvent = function() {
  this.coordinate_ = null;
  this.feature_ = null;
  return false;
};

app.map.addInteraction(new app.map.Pointer);



/**
* Interactions, Controls, and Widgets
*/

// app.map.interaction = {
//     select: {
//         segment: function() {
//             var select = new ol.interaction.Select({
//                 style: app.map.styles['LineStringSelected'],
//                 layers: [app.map.layer.streams.layer],
//                 hitTolerance: 10
//             });
//             app.map.addInteraction(select);
//             select.on('select', function(event) {
//                 app.map.layer.streams.segment.init(event);
//             });
//         },
//         pourpoint: function() {
//             var select = new ol.interaction.Select({
//                 style: app.map.styles['Point'],
//                 layers: [app.map.layer.pourpoints.layer],
//                 hitTolerance: 10,
//             });
//             app.map.addInteraction(select);
//             return select.on('select', function(event) {
//                 var collection = event.target.getFeatures();
//                 collection.forEach(function(el,i,arr) {
//                     var props = el.getProperties();
//                     console.log('%c selected: %o', 'color: #05b8c3', arr);
//                     app.request.get_basin(props.properties.id)
//                         .then(function(data) {
//                             app.request.saveState(); // save state prior to filter
//                         });
//                 });
//                 app.panel.form.init();
//                 app.state.step = 2;
//             });
//         },
//     },
//     get selection() {
//         return this.select;
//     }
// }

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
      app.map.layer.pourpoints.layer
    ],
    style: app.map.styles.LineStringSelected
  }
);
app.map.selection.selectFilterSingleClick = new ol.interaction.Select(
  {
    layers: [
      app.map.layer.huc10.layer,
      app.map.layer.huc12.layer
    ],
    style: app.map.styles.PolygonSelected
  }
);

app.map.selection.setSelect = function(selectionInteraction) {
  //Is this line necessary?
  app.map.removeInteraction(app.map.selection.select);
  app.map.selection.select = selectionInteraction;
  app.map.addInteraction(app.map.selection.select);
  app.map.selection.select.on('select', function(e) {
    console.log('selection event at ' + ol.coordinate.toStringHDMS(ol.proj.transform(
      e.mapBrowserEvent.coordinate, 'EPSG:3857', 'EPSG:4326'
    )));
    app.map.selection.select.getFeatures().forEach(function(feat) {
      var layer = app.map.selection.select.getLayer(feat);
      app.map.layer[layer.get('id')].selectAction(feat);
    });
  });
};

app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
