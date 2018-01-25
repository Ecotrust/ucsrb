app.mapbox = {
  key: 'pk.eyJ1IjoiaG9kZ2ltb3RvIiwiYSI6IjVJNU1UMWsifQ.RHNVad4mnDISsAL_B3h30Q',
};

app.map = new ol.Map({
  target: 'map',
  layers: [
    new ol.layer.VectorTile({
     declutter: true,
     name: 'Base Layer',
     source: new ol.source.VectorTile({
       attributions: '© <a href="https://www.mapbox.com/map-feedback/">Mapbox</a> ' +
         '© <a href="https://www.openstreetmap.org/copyright">' +
         'OpenStreetMap contributors</a>',
       format: new ol.format.MVT(),
       url: 'https://{a-d}.tiles.mapbox.com/v4/mapbox.mapbox-streets-v6/' +
           '{z}/{x}/{y}.vector.pbf?access_token=' + app.mapbox.key
     }),
     style: createMapboxStreetsV6Style(ol.style.Style, ol.style.Fill, ol.style.Stroke, ol.style.Icon, ol.style.Text)
   }),
   // // new ol.layer.Tile({
   //    name: 'HUC_12',
   //    source: new ol.source.XYZ({
   //      url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcqvx3v02cnr2spem8kzm7rs/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
   //    }),
   //  }),
   //  new ol.layer.Tile({
   //    name: 'HUC 10',
   //    source: new ol.source.XYZ({
   //      url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcqvt8el5jmh2sqncjcya3mx/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
   //    }),
   //  }),
   //  new ol.layer.Tile({
   //    name: 'Streams',
   //    source: new ol.source.XYZ({
   //      url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcqw3lxq3luo2spnc87wb6q8/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
   //    }),
   //  }),
   //  new ol.layer.Tile({
   //    name: 'PourPoints',
   //    source: new ol.source.XYZ({
   //      url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcqw0cln0t1t2stppz5vzd0d/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
   //    }),
   //  }),
   //  new ol.layer.Tile({
   //    name: 'Shed802',
   //    source: new ol.source.XYZ({
   //      url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcs55i2d6t0b2smjsebrise8/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
   //    }),
   //  }),
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
        console.log('yes');
      });
    },
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
      if (app.map.layer.streams.counter == 0) {
        app.map.layer.streams.data = data;
        var feature = app.map.layer.streams.feature(data);
        app.map.layer.streams.source.addFeature(feature);
        app.map.layer.streams.layer.setSource(app.map.layer.streams.source);
        app.map.addLayer(app.map.layer.streams.layer);
        app.map.layer.streams.counter++;
      } else {
        console.log('streams already added');
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
          app.map.interaction.select.pourpoint();
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
      /**
       * check if pourpoints layer has already been added
       */
      if (app.map.layer.pourpoints.counter == 0) {
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
      } else {
        console.log('streams already added');
      }
    }
  },
  huc10: new ol.layer.Tile({
    name: 'HUC 10',
    source: new ol.source.XYZ({
      // attributions: '',
      // format: new ol.format.MVT(),
      url: 'https://api.mapbox.com/styles/v1/hodgimoto/cjcl80xms0bmv2stg8k8x99k7/tiles/256/{z}/{x}/{y}@2x?access_token=' + app.mapbox.key,
    }),
  })
}
