app.mapbox = {
    key: 'pk.eyJ1IjoiaG9kZ2ltb3RvIiwiYSI6IjVJNU1UMWsifQ.RHNVad4mnDISsAL_B3h30Q',
};

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
                var collection = event.target.getFeatures();
                collection.forEach(function(el,i,arr) {
                    var props = el.getProperties();
                    app.request.get_basin(props.properties.id)
                        .then(function(data) {
                            app.request.saveState(); // save state prior to filter
                        });
                    // app.request.get_scenarios()
                        // .then(function(data) {
                        //     app.map.layer.scenarios.init();
                        // });
                    app.request.get_filter_form()
                        .then(function(data) {
                            app.state.panelContent = data // set panel state
                        });
                });
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
    }),
    scenarios: {
        layer: function() {
            return mapSettings.getInitFilterResultsLayer('scenarios', false);
        },
        source: function() {
            return app.map.layer.scenarios.layer.getSource();
        },
        init: function(data) {
            // html = '<ul>'
            // for (var i = 0; i < scenarios.length; i++) {
            //   scenario = scenarios[i];
            //   if(scenario.name == '') {
            //     scenario_name = 'Scenario ' + scenario.id;
            //   } else {
            //     scenario_name = scenario.name;
            //   }
            //   {% if SCENARIO_LINK_BASE %}
            //     scenario_link = '{{SCENARIO_LINK_BASE}}' + "_" + scenario.id;
            //   {% else %}
            //     scenario_link = "/features/scenario/scenarios_scenario_" + scenario.id;
            //   {% endif %}
            //
            //   html = html + '<li><a href="' + scenario_link + '/" target="_blank">' + scenario_name + '</a></li>';
            // }
            // html = html + '</ul>';
            // $('#scenarios').html(html)
            // {% if SCENARIO_FORM_URL %}
            //   scenario_form_url = '{{SCENARIO_FORM_URL}}';
            // {% else %}
            //   scenario_form_url = '/features/scenario/form/';
            // {% endif %}
            // app.viewModel.scenarios.createNewScenario(scenario_form_url);
        }
    },
    planningUnits: {
        layer: function() {
            return mapSettings.getInitFilterResultsLayer('planning units', app.map.styles['Polygon']);
        },
        source: function() {},
        addFeatures: function(features) {
            for(var i = 0; i < features.length; i++) {
                feature = features[i].wkt;
                app.map.layer.planningUnits.layer.addWKTFeatures(feature);
            }
            try {
                // TODO: OL Specific code!!!
                app.map.getView().fit(app.map.layer.planningUnits.layer.getExtent(), {duration: 1500});
            } catch (e) {
                window.alert('No data received. Please add some features.');
            }
        }
    },
}
