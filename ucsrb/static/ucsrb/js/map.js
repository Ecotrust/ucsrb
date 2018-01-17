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
      radius: 5,
      fill: null,
      stroke: new ol.style.Stroke({
        color: 'red',
        width: 1,
      })
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
  select: new ol.interaction.Select({
    style: app.map.styles['LineStringSelected'],
    hitTolerance: 1
  }),
  /**
   * add an interaction to the map
   * @param {Object|string} type kind of interaction or the interaction object
   */
  add: function(type) {
    if (type === 'select' || type == app.map.interaction.select) {
      app.map.addInteraction(app.map.interaction.select);
    } else {
      console.log('no interaction type given');
    }
  },
  get selection() {
    return this.select;
  }
}

app.map.popup = {}

app.map.layer = {
  streams: {
    data: {},
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
      app.map.addLayer(app.map.layer.streams.layer);
    },
    segment: {
      data: {},
      pourpoints: {
        data: {},
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        }),
        layer: new ol.layer.Vector({
          style: app.map.styles['LineString']
        }),
        show: function() {
          app.map.layer.streams.segment.pourpoints.data.forEach(function(pp,i,a) {
            var feature = new ol.Feature({
              geometry: new ol.geom.Point(pp.geometry),
              name: pp.name,
              properties: {
                id: pp.id
              }
            });
            app.map.layer.streams.segment.pourpoints.source.addFeature(feature);
            app.map.layer.streams.segment.pourpoints.layer.setSource(app.map.layer.streams.segment.pourpoints.source);
            app.map.addLayer(app.map.layer.streams.segment.pourpoints.layer);
          });
        }
      },
      set: function(data) {
        var selected = data.selected[0].getProperties();
        app.map.layer.streams.segment.data = selected;
        app.map.layer.streams.segment.pourpoints.data = selected.properties.pourpoints;
        app.map.layer.streams.segment.pourpoints.show();
      },
      select: function() {
        var select = app.map.interaction.select;
        return select.on('select', function(event) {
          app.map.layer.streams.segment.set(event);
        });
      },
    },
  },
}
