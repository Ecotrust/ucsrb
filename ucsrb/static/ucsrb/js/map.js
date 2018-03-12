app.mapbox = {
    key: 'pk.eyJ1IjoiaG9kZ2ltb3RvIiwiYSI6IjVJNU1UMWsifQ.RHNVad4mnDISsAL_B3h30Q',
};

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
            width: 20,
        }),
    }),
    'Polygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(93, 116, 82, 0.9)',
            lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 1,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(93, 116, 82, 0.45)'
        })
    }),
};

app.map.interaction = {
    select: {
        segment: function() {
            app.map.interaction.olSelect = new ol.interaction.Select({
                style: app.map.styles['LineStringSelected'],
                layers: [app.map.layer.streams.layer],
                hitTolerance: 10
            });
            app.map.addInteraction(app.map.interaction.olSelect);
            app.map.interaction.olSelect.on('select', function(event) {
                app.map.layer.streams.segment.init(event);
            });
        },
        pourpoint: function() {
            app.map.removeInteraction(app.map.interaction.olSelect);
            app.map.interaction.olSelect = new ol.interaction.Select({
                style: app.map.styles['PointSelected'],
                layers: [app.map.layer.pourpoints.layer],
                hitTolerance: 2,
            });
            app.map.addInteraction(app.map.interaction.olSelect);
            return app.map.interaction.olSelect.on('select', function(event) {
                var collection = event.target.getFeatures();
                collection.forEach(function(el,i,arr) {
                    var props = el.getProperties();
                    console.log('%c selected: %o', 'color: #05b8c3', arr);
                    app.request.get_basin(props.properties.id)
                        .then(function(data) {
                            app.request.saveState(); // save state prior to filter
                        });
                });
                app.panel.form.init();
                app.state.step = 2;
            });
        },
    },
    draw: {
        source: new ol.source.Vector(),
        layer: new ol.layer.Vector({
            style: app.map.styles['Polygon'],
        }),
        init: function() {
            app.map.interaction.draw.layer.setSource(app.map.interaction.draw.source);
            app.map.addLayer(app.map.interaction.draw.layer);
            app.map.interaction.draw = new ol.interaction.Draw({
                source: app.map.interaction.draw.source,
                type: 'Polygon',
            });
            app.map.addInteraction(app.map.interaction.draw);
        },
    }
}

app.map.popup = {}

/**
* Map - Layers, Sources, Features
*/
app.map.layer = {
    streams: {
        data: {}, // store init data
        counter: 0, // so layer is only added once
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
            // Check if layer has already been added
            if (app.map.layer.streams.counter === 0) {
                app.map.layer.streams.data = data;
                var feature = app.map.layer.streams.feature(data);
                app.map.layer.streams.source.addFeature(feature);
                app.map.layer.streams.layer.setSource(app.map.layer.streams.source);
                app.map.addLayer(app.map.layer.streams.layer);
                app.map.layer.streams.counter++;
            } else {
                console.log('%cstreams already added', 'color: orange;');
            }
        },
        segment: {
            data: {}, // store init data
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
        data: {}, // store init data
        counter: 0, // so layer is only added once
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
            // Check if layer has already been added
            if (app.map.layer.pourpoints.counter === 0) {
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
                app.state.step = 1; // step forward in state
            } else {
                console.log('%cstreams already added', 'color: orange');
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
    demo_basin: new ol.layer.Tile({
        name: 'basin',
        source: new ol.source.XYZ({
            url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcs55i2d6t0b2smjsebrise8/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
        }),
    }),
    demo_pourpoint: new ol.layer.Tile({
        name: 'pourpoint',
        source: new ol.source.XYZ({
            url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcs6xklx0vqi2rp5ib93ogeh/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
        }),
    }),
    demo_stream: new ol.layer.Tile({
        name: 'stream',
        source: new ol.source.XYZ({
            url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcs7bpiu6uzl2so8svgny8bl/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
        }),
    }),
    demo_streams: new ol.layer.Tile({
        name: 'streams',
        source: new ol.source.XYZ({
            url: 'https://api.mapbox.com/styles/v1/ucsrbsupport/cjcqw3lxq3luo2spnc87wb6q8/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidWNzcmJzdXBwb3J0IiwiYSI6ImNqY3Fzanl6cDAxaGgzM3F6ZXVqeHI0eTYifQ.7T_7fsmV6QIuh_9EEo0wMw'
        }),
    }),
    scenarios: {
        counter: 0, // so layer is only added once
        layer: mapSettings.getInitFilterResultsLayer('scenarios', false),
        source: function() {
            return app.map.layer.scenarios.layer.getSource();
        },
        init: function(data) {
            if (app.map.layer.scenarios.counter < 1) {
                app.map.addLayer(app.map.layer.scenarios.layer);
                app.request.get_scenarios()
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
                app.map.addLayer(app.map.layer.planningUnits.layer);
                app.request.get_planningunits()
                    .then(function(response) {
                        app.map.layer.planningUnits.addFeatures(response);
                    });
                app.map.layer.planningUnits.counter++;
            } else {
                console.log('%cplanning unit layer already added', 'color: orange');
            }
        }
    },
}
