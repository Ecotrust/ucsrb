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

app.map.interaction = {
  select: new ol.interaction.Select(),
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

app.map.styles = {
  'Point': new ol.style.Style({
    image: new ol.style.Circle({
      radius: 5,
      fill: null,
      stroke: new ol.style.Stroke({
        color: 'red',
        width: 1
      })
    })
  }),
  'LineString': new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: '#3399dd',
      width: 10
    })
  }),
  'Polygon': new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: 'blue',
      lineDash: [4],
      width: 3
    }),
    fill: new ol.style.Fill({
      color: 'rgba(0, 0, 255, 0.1)'
    })
  }),
};

app.map.popup = {}

app.map.layer = {
  streams: {
    data: {},
    pourpoints: [],
    source: new ol.source.Vector({
        format: new ol.format.GeoJSON()
    }),
    layer: new ol.layer.Vector({
      style: app.map.styles['LineString']
    }),
    init: function(data) {
      app.map.layer.streams.data = data;
      app.map.layer.streams.pourpoints = data.pourpoints;
      app.map.layer.streams.feature = new ol.Feature({
        geometry: new ol.geom.LineString(data.geometry.geometry.coordinates),
        name: data.name
      });
      app.map.layer.streams.source.addFeature(app.map.layer.streams.feature);
      app.map.layer.streams.layer.setSource(app.map.layer.streams.source);
      app.map.addLayer(app.map.layer.streams.layer);
    },
    selectListener: function() {
      var select = app.map.interaction.select;
      select.on('select', function(e) {
        console.log('selected stream');
      });
    }
  },
}
