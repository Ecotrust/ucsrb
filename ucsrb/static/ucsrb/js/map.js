app.map = new ol.Map({
  target: 'map',
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM()
    }),
  ],
  view: new ol.View({
    center: [-13405984.640957793,6046804.319313334],
    zoom: 8
  })
});

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
      color: 'rgba(0, 0, 255, 0.1)'
    })
  }),
};

app.map.interaction = {
  select: {
    segment: function() {
      var select = new ol.interaction.Select({
        style: app.map.styles['LineStringSelected'],
        hitTolerance: 1
      });
      return select.on('select', function(event) {
        app.map.layer.streams.segment.init(event);
      });
    },
    pourpoint: function() {
      var select = new ol.interaction.Select({
        style: app.map.styles['Point'],
        hitTolerance: 1,
      });
      return select.on('select', function(event) {
        console.log('yes');
      });
    },
  },
  /**
   * add an interaction to the map
   * @param {Object|string} type kind of interaction or the interaction object
   */
  add: function(type) {
    if (type === 'select' || type == app.map.interaction.select.segment) {
      app.map.addInteraction(app.map.interaction.select.segment);
    } else {
      console.log('no interaction type given');
    }
  },
  get selection() {
    return this.select;
  }
}

app.map.popup = {}

/**
 * Map - Layers, Sources, Features
 */
app.map.layer = {
  streams: {
    data: {},
    counter: 0,
    source: new ol.source.Vector({
        format: new ol.format.GeoJSON()
    }),
    layer: new ol.layer.Vector({
      style: app.map.styles['LineString']
    }),
    init: function(data) {
      app.map.layer.streams.data = data;
      app.map.layer.streams.features = new ol.Feature({
        geometry: new ol.geom.LineString(data.geometry.geometry.coordinates),
        name: data.name,
        properties: {
          id: data.id,
          pourpoints: data.pourpoints
        }
      });
      app.map.layer.streams.source.addFeature(app.map.layer.streams.features);
      app.map.layer.streams.layer.setSource(app.map.layer.streams.source);
      /**
       * check if streams layer has already been added
       */
      if (app.map.layer.streams.counter < 1) {
        app.map.addLayer(app.map.layer.streams.layer);
      } else {
        app.map.layer.streams.counter++;
      }
    },
    segment: {
      data: {},
      init: function(data) {
        if (data.selected.length > 0) {
          var selected = data.selected[0].getProperties();
          app.map.layer.streams.segment.data = selected;
          app.map.layer.pourpoints.data = selected.properties.pourpoints;
          app.map.layer.pourpoints.init();
        }
      },
    },
  },
  pourpoints: {
    data: {},
    counter: 0,
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
      /**
       * check if pourpoints layer has already been added
       */
      if (app.map.layer.pourpoints.counter < 1) {
        app.map.addLayer(app.map.layer.pourpoints.layer);
      } else {
        app.map.layer.pourpoints.counter++;
      }
    }
  },
}
