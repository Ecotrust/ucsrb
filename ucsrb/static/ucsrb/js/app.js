var app = {
    /**
    * set app state for process method
    * init a process method
    * @param {string} method value from data-attr on html element
    */
    setState: function(method) {
        app.state.setMethod = method;
        app.init[method]();
    },
    scenarioInProgress: function() {
        if (app.state.step === 0 || app.state.method === 'reset') {
            return false;
        } else if (app.state.step === 1 && app.state.method === 'filter') {
            return false;
        } else {
            return true;
        }
    },
    promptToSave: function() {
        console.log('Save before starting over?');
    }
}

scenario_type_selection_made = function(selectionType) {
    var animateObj = {
        zoom: 8,
        center: [-13363592.377434019, 6154762.569701998],
        duration: 800
    }
    // var extent = new ol.extent.boundingExtent([[-121.1, 47], [-119, 49]]);
    // extent = ol.proj.transformExtent(extent, ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
    if (selectionType === 'draw') {
        app.map.layer.draw.layer.setVisible(true);
        // app.map.removeInteraction(app.map.Pointer);
        // app.map.getView().animate(animateObj);
    } else {
        app.map.removeInteraction(app.map.draw.draw);
        app.map.layer.draw.layer.setVisible(false);
        // app.map.addInteraction(app.map.Pointer);
        // app.map.getView().animate(animateObj);
    }
}

baseInit = function() {
    app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
    app.map.closePopup();
    app.map.draw.disable();
    app.map.popupLock = false;
    app.map.setBoundaryLayer(app.map.layer.boundary.layer);
}

setInit = function() {
    baseInit();
    if (app.map.hasOwnProperty('mask')) {
        app.map.mask.set('active', false);
    }
    app.map.clearLayers();
    app.map.enableLayer('boundary');

    app.state.setStep = 0;
    app.map.layer.draw.layer.getSource().clear();
};

reportInit = function() {

}

app.init = {
    'select': function() {
        setInit();
        app.map.selection.setSelect(app.map.selection.selectSelectSingleClick);
        app.map.enableLayer('streams');
        scenario_type_selection_made('select');
    },
    'filter': function() {
        setInit();
        app.map.selection.setSelect(app.map.selection.selectFilterSingleClick);
        // app.map.enableLayer('huc12');
        scenario_type_selection_made('filter');
    },
    'draw': function() {
        setInit();
        // app.map.enableLayer('huc10');
        app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
        scenario_type_selection_made('draw');
    },
    'hydro': function() {
        reportInit();
        app.state.setStep = 'hydro';
        app.panel.results.showHydro();
    },
    'aggregate': function() {
        reportInit();
        app.state.setStep = 'aggregate';
        app.panel.results.showAggregate();
    }
}

app.resultsInit = function(id) {
    app.map.geoSearch.closeSearchBox();
    app.panel.results.init();
    if (!id) {
        id = app.viewModel.scenarios.scenarioList()[0].uid;
    } else if (!id.includes('ucsrb')) {
        id = 'ucsrb_treatmentscenario_' + id;
        app.viewModel.scenarios.addScenarioToMap(null, {
            uid: id
        });
    }
    app.loadingAnimation.panel.show();
    app.request.get_results(id,false)
        .done(function(response) {
            app.panel.results.responseResultById(response);
            app.map.layer.resultPoints.layer.getSource().clear();
            var layerAdded = false;
            app.map.getLayers().forEach(function(i) {
                if (i.get('id') === 'resultPoints') {
                    layerAdded = true;
                }
            });
            if (!layerAdded) {
                app.map.addLayer(app.map.layer.resultPoints.layer);
            }
            // run this after function is called for performance
            window.setTimeout(function() {
              app.map.setBoundaryLayer(app.map.layer.boundary.layer);
              app.map.layer.boundary.layer.setVisible(true);
              app.map.addFocusAreaToMap(response.focus_area);
              app.map.addDownstreamPptsToMap(response.pourpoints);
            }, 500);
        })
        .catch(function(response) {
            console.log('%c failed to get results: %o', 'color: salmon;', response);
        });
    app.nav.hideSave();
    app.nav.showResultsNav();
    $('#subnav-sign-in-modal').addClass('d-none');
}

initFiltering = function() {
    setTimeout(function() {
        if ($('#focus_area_accordion').length > 0) {
            $('#id_focus_area').prop('checked', true);
            $('#id_focus_area_input').val(app.state.focusAreaState.id);
            $('#focus_area_accordion').hide();
            app.viewModel.scenarios.scenarioFormModel.toggleParameter('focus_area');
        } else {
            initFiltering();
        }
    }, 300);
};

drawingIsSmallEnough = function(areaInMeters) {
    maxAcres = app.map.draw.maxAcres;
    metersPerAcre = 4046.86;
    return maxAcres*metersPerAcre > areaInMeters;
}

app.panel = {
    hide: function() {
        app.panel.element.hidden = true;
        app.nav.hideSave();
    },
    show: function() {
        app.panel.element.hidden = false;
    },
    loading: {
        show: function() {
            $('.panel .loading-animation').removeClass('hide');
            $('.panel .loading-animation').addClass('show');
        },
        hide: function() {
            $('.panel .loading-animation').removeClass('show');
            $('.panel .loading-animation').addClass('hide');
        }
    },
    moveLeft: function() {
        app.panel.show();
        app.panel.getElement.classList.add('left');
        app.panel.getElement.classList.remove('right');
        app.state.panel.position = 'left'; // set state
    },
    moveRight: function() {
        app.panel.show();
        app.panel.getElement.classList.add('right');
        app.panel.getElement.classList.remove('left');
        app.state.panel.position = 'right'; // set state
    },
    setContent: function(content) {
        app.panel.show();
        app.state.panel.content = content;
        app.panel.getPanelContentElement.innerHTML = content;
    },
    toggleSize: function() {
        var appPanel = app.panel.getElement;
        if (appPanel.classList.contains('expanded')) {
            appPanel.classList.remove('expanded');
        } else {
            appPanel.classList.add('expanded');
        }
        if (app.panel.results.chart.obj) {
            app.panel.results.chart.resize();
        }
    },
    form: {
        init: function() {
            app.panel.moveRight();
            app.panel.form.scenario = app.viewModel.scenarios.createNewScenario('/features/treatmentscenario/form/');
            // app.nav.showSave();
            initFiltering();
        },
    },
    summary: {
        init: function() {
            document.getElementById('chartResult').innerHTML = app.panel.results.styleSummaryResultsAsRows(app.panel.results.summary);
        }
    },
    results: {
        init: function() {
            app.panel.getPanelContentElement.innerHTML = app.nav.stepActions.initial;
            app.panel.moveLeft();
            if (app.state.nav === 'tall') {
                app.state.navHeight = 'short';
            }
        },
        name: '',
        responseResultById: function(result) {
            app.panel.results.aggPanel(result);
            app.init['aggregate']();
            app.panel.results.hydroPanel('Select a gauging station to see hydrologic results.');
        },
        loadHydroResult: function(result) {
            app.panel.results.hydroPanel(result);
            app.panel.results.showHydro();
        },
        addResults: function(content, callback) {
            app.panel.results.getPanelResultsElement.innerHTML += content;
            app.panel.results.expander();
            if (callback) {
                callback();
            }
        },
        addHydroResults: function(content, callback) {
            if (document.getElementById('hydro-results')) {
                $('#hydro-results').replaceWith(content);
            } else {
                app.panel.results.addResults(content);
            }
            if (callback) {
              callback();
            }
        },
        showAggregate: function() {
            $('.result-section').removeClass('show');
            $('#aggregate-results').addClass('show');
        },
        showHydro: function() {
            if (!document.getElementById('hydro-results')) {
                $('.result-section').removeClass('show');
                $('#hydro-note').addClass('show');
            } else {
                $('.result-section').removeClass('show');
                $('#hydro-results').addClass('show');
            }
        },
        expander: function() {
            if (!document.querySelector('#expand')) {
                app.panel.getPanelContentElement.insertAdjacentHTML('afterbegin', '<a id="expand" href="#" onclick="app.panel.toggleSize()" /><img src="/static/ucsrb/img/icon/i_expand.svg" alt="expand" /></a>');
            }
        },
        aggPanel: function(results) {
            app.panel.results.name = results.scenario.name;
            var html = `<section class="aggregate result-section" id="aggregate-results">`;
            html += `<div class="media align-items-center">
            <img class="align-self-center mr-3" src="/static/ucsrb/img/icon/i_pie_chart.svg" alt="aggregate">
                <div class="media-body">
                    <h4 class="mt-2 mb-2">${app.panel.results.name}</h4>
                </div>
            </div>`;
            html += `<div class="feature-result"><span class="lead">${results.scenario.acres}</span> acres</div><div class="overflow-gradient"><div class="result-list-wrap align-items-center">`;
            for (var result of results.aggregate_results) {
                html += `<h5>${Object.keys(result)}</h5>`;
                html += app.panel.results.styleResultsAsRows(Object.values(result));
            }
            html += '</div></div>';
            // html += `<div class="download-wrap"><button class="btn btn-outline-primary">Download</button></div>`
            html += '</section>';
            app.panel.results.addResults(html);
        },
        hydroPanel: function(results) {
            if (typeof(results) === 'string') {
                var html = `<section class="hydro-results result-section" id="hydro-note">`;
                html += `<div>${results}</div>`;
                html += `</section>`;
                app.panel.results.addResults(html);
                return;
            }
            // charts array
            app.panel.results.charts = []
            app.panel.results.summary = []
            var html = `<section class="hydro-results result-section" id="hydro-results">`;
                html += `<div id="pp-result" class="pourpoint-result-wrap"><div class="media align-items-center"><img class="align-self-center mr-3" src="/static/ucsrb/img/icon/i_hydro.svg" alt="aggregate"><div class="media-body"><h4 class="mt-0">${app.panel.results.name}</h4></div></div></div>`;

                html += `<div class="feature-result dropdown-wrap"><div class="dropdown"><button class="btn btn-link dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select Chart</button>`;
                html += `<div class="dropdown-menu dropdown-menu-center" id="chart-dropdown" aria-labelledby="dropdownMenuButton">`
                for (var result in results.results) {
                    // load into charts array
                    var resultObj = results.results[result];
                    if (resultObj.type != 'Summary') {
                        for (var report in results.results[result].reports) {
                            var reportObj = results.results[result].reports[report];
                            app.panel.results.charts.push(reportObj);
                            html += `<button class="dropdown-item btn-sm" id="chart-${report}" data-chart="${reportObj.title}" onclick="app.panel.results.chart.init(${report})" type="button">${reportObj.title}</button>`;
                        }
                    } else {
                        for (var report in resultObj.reports) {
                            var reportObj = results.results[result].reports[report];
                            app.panel.results.summary.push(reportObj);
                        }
                        html += `<button class="dropdown-item btn-sm" id="chart-summary" data-chart="Summary" onclick="app.panel.summary.init()" type="button">Summary</button>`;
                    }
                }
                html += `</div></div></div>`;
                html += `<div class="chart-wrap"><div id="chartResult"></div></div>`;
            html += '</section>';
            // html += `<div class="download-wrap"><button class="btn btn-outline-primary">Download</button></div>`
            app.panel.results.addHydroResults(html, function() {
                $('.dropdown').on('click', function(event) {
                    var chartName = event.target.dataset.chart;
                    $(this).find('#dropdownMenuButton').text(chartName);
                    $(this).find('button').removeClass('active');
                    event.target.classList.add('active');
                });
                $('#chart-summary').click();
            });

            app.panel.loading.hide();
        },
        styleResultsAsRows: function(results) {
            var html = '<div class="table-responsive"><table class="table-light table-borderless table"><tbody>';
            for (var result in results) {
                html += '<tr>'
                for (var i = 0; i < results[result].length; i++) {

                  for (var j=0; j < Object.keys(results[result][i]).length; j++){
                    html += `<tr><td>${Object.keys(results[result][i])[j]}</td><td>${Object.values(results[result][i])[j]}</td></tr>`;
                  }
                }
                html += '</tr>'
            }
            html += '</tr></tbody></table></div>'
            return html;
        },
        styleSummaryResultsAsRows: function(results) {
          var html = '<h2>Summary Report</h2>';
          for (var result in results) {
              html += `<h3>${results[result].title}</h3>`
              html += '<div class="table-responsive"><table class="table-light table-borderless table"><tbody>';
              // html += '<tr><th>Field</th><th>Value</th><th>Unit</th></tr>';
              for (var i = 0; i < results[result].data.length; i++) {
                html += `<tr><td>${results[result].data[i]["key"]}</td><td>${results[result].data[i]["value"]}</td><td>${results[result].data[i]["unit"]}</td></tr>`;
              }
              html += '</tbody></table></div>'
          }
          return html;
        },
        chart: {
            init: function(chartIndex) {
                app.panel.loading.show();
                var chartJSON = {};
                var data = app.panel.results.charts[chartIndex].data;
                for (var chart in data) {
                    resultsArray = [];
                    if (chart !== 'baseline') {
                        chartJSON.timestep = [];
                        for (var i = 0; i < data[chart].length; i++) {
                            resultsArray.push(data[chart][i].flow);
                            chartJSON.timestep.push(data[chart][i].timestep);
                        }
                    } else {
                        chartJSON.timestep = [];
                        for (var i = 0; i < data[chart].length; i++) {
                            resultsArray.push(data[chart][i].flow);
                            chartJSON.timestep.push(data[chart][i].timestep);
                        }
                    }
                    chartJSON[chart] = resultsArray;
                }
                app.panel.results.chart.obj = bb.generate({
                    data: {
                        json: chartJSON,
                        x: 'timestep',
                        xFormat: '%m.%d.%Y-%H:%M:%S',
                        names: {
                            flow: 'CFPS'
                        },
                        type: 'line',
                        colors: {
                            baseline: '#394861',
                            'reduce to 30': '#FB7302',
                            'reduce to 0': '#680109',
                            'reduce to 50': '#93A35D',
                        }
                    },
                    axis: {
                        x: {
                            show: true,
                            inner: false,
                            type: 'timeseries',
                            tick: {
                                count: 12,
                                culling: false,
                                fit: false,
                                outer: true,
                                format: function(val) {
                                    var fval = d3.timeFormat('%b')(val);
                                    return fval.substring(0,1);
                                },
                            },
                            label: 'Month',
                        },
                        y: {
                            show: true,
                            inner: true,
                            label: 'CFS',
                        }
                    },
                    zoom: {
                        enabled: true,
                        rescale: true,
                    },
                    subchart: {
                        show: true,
                        size: {
                             height: 40
                         },
                    },
                    point: {
                        show: false,
                    },
                    // legend: {
                    //     position: 'inset',
                    //     inset: {
                    //         anchor: 'top-right'
                    //     }
                    // },
                    tooltip: {
                        format: {
                            title: function(x) {
                                return d3.timeFormat("%B %d @ %-I %p")(x);
                            },
                            value: function(value, ratio, id) {
                                value = value.toFixed(4);
                                return value;
                            }
                        }
                    },
                    padding: {
                        left: 8,
                        right: 8
                    },
                    bindto: `#chartResult`
                });
                app.panel.results.chart.resize();
                app.panel.loading.hide();
            },
            resize: function() {
                window.setTimeout(function() {
                    app.panel.results.chart.obj.resize();
                }, 300);
            }
        },
        panelResultsElement: function() {
            return this.getPanelResultsElement;
        },
        get getPanelResultsElement() {
            return document.getElementById('results');
        }
    },
    draw: {
        setContent: function(content) {
            app.panel.show();
            app.state.panel.content = content;
            app.panel.draw.getDrawContentElement.innerHTML = content;
        },
        finishDrawing: function() {
            app.panel.moveRight();
            window.setTimeout(function() {
                var drawingArea = app.map.draw.getDrawingArea();
                var drawingAcres = drawingArea/4046.86;
                var saveDisable = 'disabled';
                var warning = '<p><em>must be under ' + app.map.draw.maxAcres.toString() + '</em></p>';
                if (drawingIsSmallEnough(drawingArea)) {
                    saveDisable = '';
                    warning = '';
                }
                var html = '<div class="featurepanel">' +
                '<p class="display"><span class="bb">' + drawingAcres.toFixed(0).toString() + '</span> acres selected</p>' +
                warning +
                '<p><small>Click the map to start a new drawing<br />Re-select point to edit<br />Select drawing boundary to alter<br />Alt+Select point to delete</small></p>' +
                '<form id="draw_submit_form" onsubmit="app.panel.draw.saveDrawing(); return false;">' +
                '<label for="treat_name">Treatment Name:</label>' +
                '<input type="text" name="treat_name" required><br>' +
                '<label for="treat_desc">Description:</label>' +
                '<textarea rows="2" columns="35" name="treat_desc"></textarea><br>' +
                '<br>' +
                '<div class="btn-toolbar justify-content-between drawing-buttons">' +
                '<button type="submit" class="btn btn-primary ' + saveDisable + '" >Begin Evaluation</button>' +
                '<button type="button" class="btn btn-outline-secondary" onclick="app.panel.draw.restart()">Restart</button>' +
                '</div>' +
                '</form>' +
                '</div>';
                app.panel.draw.setContent(html);
            }, 300);
        },
        restart: function() {
            app.map.draw.source.clear();
            app.map.draw.disable();
            app.map.draw.enable();
            app.panel.hide();
            app.panel.draw.finishDrawing();
        },
        addTreatmentArea: function() {
            app.map.draw.enable();
            var html = '<div class="featurepanel">' +
            '<h4>Click on the map to start drawing your new forest management scenario.</h4>' +
            '<div class="btn-toolbar justify-content-between drawing-buttons">' +
            '<button type="button" class="btn btn-light" onclick="app.panel.draw.cancelDrawing()">Cancel</button>' +
            '</div>' +
            '</div>';
            app.panel.draw.setContent(html);
        },
        cancelDrawing: function() {
            app.map.draw.disable();
            app.panel.draw.finishDrawing();
        },
        acceptDrawing: function() {
            var html = '<div class="featurepanel">' +
            '<h4>Do you want to harvest within this treatment area?</h4>' +
            '<div class="btn-toolbar justify-content-between drawing-buttons">' +
            '<button type="button" class="btn btn-light" onclick="app.panel.draw.saveDrawing()">Yes, I\'m Done</button>' +
            '<button type="button" class="btn btn-light" onclick="app.panel.draw.finishDrawing()">No, Change This</button>' +
            '</div>' +
            '</div>';
            app.panel.draw.setContent(html);
        },
        saveDrawing: function() {
            var drawFeatures = app.map.draw.source.getFeatures();
            totalArea = 0;
            for (var i = 0; i < drawFeatures.length; i++) {
                totalArea += ol.Sphere.getArea(drawFeatures[i].getGeometry());
            }
            if (drawingIsSmallEnough(totalArea)) {
                var drawing_name = $('#draw_submit_form').find('[name=treat_name]').val();
                var drawing_desc = $('#draw_submit_form').find('[name=treat_desc]').val();
                app.request.saveDrawing(drawing_name, drawing_desc);
            } else {
                areaInAcres = totalArea/4046.86;
                alert('Your treatment area is too large (' + areaInAcres.toFixed(0) + ' acres). Please keep it below ' + app.map.draw.maxAcres.toString() + ' acres');
                app.panel.draw.acceptDrawing();
            }
        },
        get getDrawContentElement() {
            return document.getElementById('draw_form');
        }
    },
    element: function() { // returns a function. to edit dom element don't forget to invoke: element()
    return this.getElement;
    },

    panelContentElement: function() { // returns a function. to edit dom element don't forget to invoke: panelContentElement()
      return this.getPanelContentElement;
    },
    get getElement() {
        return document.getElementById('panel');
    },
    get getPanelContentElement() {
        return document.getElementById('panel-content');
    }
}

enableDrawing = function() {
    app.map.draw.enable();
    app.map.geoSearch.openSearchBox();
}

app.filterDropdownContent = `<div class="dropdown">
        <button class="btn btn-sm ml-2 btn-outline-light dropdown-toggle" type="button" id="forestUnit" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select unit</button>
        <div class="dropdown-menu forest-unit-dropdown" aria-labelledby="forestUnit">
            <div id="forest-listener">
                <button class="dropdown-item" type="button" data-layer="huc10">HUC 10</button>
                <button class="dropdown-item" type="button" data-layer="huc12">HUC 12</button>
                <button class="dropdown-item" type="button" data-layer="RMU">Forest Plan Mgmt Alloc</button>
            </div>
        </div>
    </div>
    <script>
        (function() {
            $('#forest-listener button').on('click', function(event) {
                event.preventDefault();
                $('#forest-listener').children().each(function(i) {
                    if ($(this)[0].dataset.layer !== event.target.dataset.layer) {
                        app.map.disableLayer($(this)[0].dataset.layer);
                    }
                });
                var eventLayer = event.target.dataset.layer;
                app.map.toggleLayer(eventLayer);
                app.state.setStep = 1;
            });
        })();
    </script>`;

app.nav = {
    setState: function(height) {
        app.state.navHeight = height;
    },
    showResultsNav: function() {
        document.getElementById('results-nav').classList.remove('d-none');
        document.getElementById('process-nav').classList.add('d-none');
        document.querySelectorAll('#file-nav .results-nav-item').forEach(function(i, arr) {
            i.classList.remove('d-none')
        });
    },
    hideResultsNav: function() {
        document.getElementById('results-nav').classList.add('d-none');
        document.getElementById('process-nav').classList.remove('d-none');
        document.querySelectorAll('#file-nav .results-nav-item').forEach(function(i, arr) {
            i.classList.add('d-none')
        });
    },
    showStartOver: function() {
        document.getElementById('nav-start-over').classList.remove('d-none');
    },
    showSave: function() {
        document.getElementById('nav-anon-save').classList.remove('d-none');
    },
    saveElement: function() {
        return document.getElementById('nav-anon-save');
    },
    showAnonSave: function() {
        document.getElementById('subnav-sign-in-modal').classList.remove('d-none');
    },
    hideSave: function() {
        document.getElementById('nav-anon-save').classList.add('d-none');
    },
    short: function() {
        // style nav
        $('.nav-wrap').addClass('icons-only');
        $('.map-wrap').addClass('short-nav');
        $('.overlay').addClass('fade-out short-overlay');
        setTimeout(function() {
            $('#process-nav').addClass('justify-content-start');
            $('#process-nav').removeClass('justify-content-center');
            $('.overlay').removeClass('fade-out');
        }, 1000);
    },
    tall: function() {
        $('.nav-wrap').removeClass('icons-only');
        $('.nav-wrap').removeClass('short-nav');
        setTimeout(function() {
            $('#process-nav').removeClass('justify-content-start');
            $('#process-nav').addClass('justify-content-center');
        }, 1000);
    },
    instructions: {
        initial: `<h2 class="mx-auto w-50 text-center">Start by deciding how you want <br/>to interact with the map</h2>`,
        reset: `Decide how you want to interact with the map`,
        select: [
            'Zoom in and select a stream segment to evaluate changes in flow',
            'select one of the highlighted pour points to evaluate changes in flow associated with management activity upstream',
            'Select filters to narrow your treatment region',
        ],
        filter: [
            `Select area to manage based on: ${app.filterDropdownContent}`,
            `Select forest unit to filter or change selection: ${app.filterDropdownContent}`,
            'Select filters to narrow your treatment area',
        ],
        draw: [
            'Zoom in to area of interest or use the geocoder to search for places by name.<br />Click on the map to start drawing the boundary of your management area.',
            'Add additional points then double-click to finish; Re-select point to edit',
        ],
        result: 'Explore evaluation results',
        aggregate: 'Select virtual gauging station ( <span style="height: 20px; background: #fff; border: 2px solid #67b8c6; border-radius: 50%; box-shadow: 0 0 4px #333, 0 0 4px #999; width: 20px; margin: 4px 10px; display: inline-block;"></span> ) to view predicted changes in flow.',
        hydro: 'Your hydrologic results',
    },
    stepActions: {
        initial: '<div id="scenarios"></div><div id="scenario_form"></div><div id="draw_form"></div><div id="results"></div>',
        reset: function() {
            app.panel.getPanelContentElement.innerHTML = app.nav.stepActions.initial;
            app.panel.moveRight();
            app.nav.hideSave();
            app.map.removeLayer(app.map.layer.selectedFeature.layer);
            app.map.removeLayer(app.map.layer.resultPoints.layer);
            app.map.geoSearch.closeSearchBox();
            if (app.map.mask) {
                app.map.mask.set('active', false);
            }
            closeConfirmSelection(true,true);
        },
        select: [
            false,
            false,
            app.panel.form.init
        ],
        filter: [
            false,
            false,
            app.panel.form.init
        ],
        draw: [
            enableDrawing,
            false     //TODO: ??? enable editing?
        ],
        results: function() {
            app.nav.hideSave();
            if (app.state.nav !== 'short') {
                app.state.navHeight = 'short';
            }
        },
        aggregate: function() {
            // Trigger a click on navigation so arrow appears
            $('button[data-method=aggregate]').click()

        },
        hydro: function() {
            $('button[data-method=hydro]').click()
        }
    }
}

app.loadingAnimation = {
    show: function() {
        $('#loading-modal').modal('show');
    },
    hide: function() {
        $('#loading-modal').modal('hide');
    },
    panel: {
        show: function() {

        },
        hide: function() {

        }
    }
}
// using jQuery to get CSRF Token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/**
* Application AJAX requests object and methods
* {get_results} results for treatment scenario
* {get_segment_by_bbox} segment by bounding box
* {get_segment_by_id} segment by id
* {get_pourpoint_by_id} pourpoint by id
* {filter_results} filter results
*
*/
app.request = {
    /**
    * get results for treatment scenario
    * @param  {[number]} id treatment scenario id [on scenario this is created]
    * @return {[json]} result data
    */
    get_results: function(id,exportResults) {
        if (!id) {
            id = app.map.selectedFeature.getProperties().ppt_ID;
        }
        return $.ajax({
            url: `/get_results_by_scenario_id`,
            data: {
                id: id,
                // export: exportResults
            },
            dataType: 'json',
            success: function(response) {
                return response;
            },
            error: function(response) {
                console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
            }
        })
    },
    get_downstream_pour_points: function(id) {
        if (!id) {
            id = app.map.selectedFeature.getProperties().ppt_ID;
        }
        return $.ajax({
            url: `/get_downstream_pour_points`,
            data: {
                pourpoint_id: id
            },
            dataType: 'json',
            success: function(response) {
                return response;
            },
            error: function(response) {
                console.log(`%cfail @ get downstream pourpoints: %o`, 'color: red', response);
            }
        })
    },
    get_hydro_results_by_pour_point_id: function(feature, scenarioId) {
        if (feature.getProperties().ppt_ID) {
            var pp_id = feature.getProperties().ppt_ID;
        } else if (feature.getProperties().id) {
            var pp_id = feature.getProperties().id;
        } else {
            var pp_id = feature.getProperties().ppt_id
        }
        app.map.selectedPourPoint = feature;
        if (!scenarioId) {
            treatmentId = app.state.scenarioId;
        }
        return $.ajax({
            url: '/get_hydro_results_by_pour_point_id',
            data: {
                pourpoint_id: pp_id,
                treatment_id: treatmentId,
            },
            dataType: 'json',
            success: function(response) {
                return response;
            },
            error: function(response) {
                console.log(`%cfail @ get hydro results for pourpoint: %o`, 'color: red', response);
            }
        });
    },
    /**
    * Planning Units
    * scenario planning units to filter upon
    * @return {[json]} features list
    */
    get_planningunits: function() {
        return $.ajax('/scenario/get_planningunits')
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
        });
    },
    get_user_scenarios: function() {
        return $.ajax('/get_user_scenario_list/')
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ get scenarios: %o`, 'color: red', response);
        });
    },
    get_scenarios: function() {
        return $.ajax('/ucsrb/get_scenarios/')
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ get scenarios: %o`, 'color: red', response);
        });
    },
    /**
    * get stream segments by bounding box
    * @param {Array} bbox coords from map view
    */
    get_segment_by_bbox: function(bbox) {
        return $.ajax({
            url: `/get_segment_by_bbox`,
            data: {
                bbox_coords: bbox
            },
            dataType: 'json'
        })
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ get segment by bbox: %o`, 'color: red', response);
            return false;
        });
    },
    /**
    * Request stream segement by id
    * @param {number|int} id
    * @returns {Object} stream segement
    * @property segment name id geometry pourpoints[id, geometry, name]
    */
    get_segment_by_id: function(id) {
        return $.ajax(`/segment/${id}`)
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ segment by id: %o`, 'color: red', response);
        });
    },
    /**
    * Request pourpoint by id
    * @param {number|int} id
    * @returns {Object} pourpoint
    * @property name id acres point_geometry area_geometry
    */
    get_pourpoint_by_id: function(id) {
        return $.ajax(`pourpoint/${id}`)
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ get pourpoint id: %o`, 'color: red', response);
        });
    },
    get_focus_area: function(feature, callback) {
        app.map.selectedFeature = feature;
        var props = app.map.selectedFeature.getProperties();
        var layer = app.mapbox.layers[props.layer.split('.shp')[0]].map_layer_id;
        var idField = app.mapbox.layers[props.layer.split('.shp')[0]].id_field;
        var id = props[idField];
        return $.ajax({
            url: '/ucsrb/get_focus_area',
            data: {
                id: id,
                layer: layer,
            },
            dataType: 'json',
            success: function(response) {
                app.state.setFocusArea = response;
                callback(feature, response.geojson);
            },
            error: function(response, status) {
                console.log(`%cfail @ get focus area: %o`, 'color: red', response);
                callback(null, response);
                return status;
            }
        })
    },
    get_focus_area_at: function(feature, layerName, callback) {
        /**
        * This is sloppy, but I don't know how to get the geometry from a VectorTile feature.
        * @todo {Priority low} find try and set geometry from vector tile
        */
        point = feature.getFlatCoordinates();
        return $.ajax({
            url: '/ucsrb/get_focus_area_at',
            data: {
                point: point,
                layer: layerName,
            },
            dataType: 'json',
            success: function(response) {
                callback(feature, response);
            },
            error: function(response, status) {
                console.log(`%cfail @ get focus area at point: %o`, 'color: red', response);
                callback(null, response);
            }
        })
    },
    /**
    * get a pourpoint's basin
    * @param  {number} pp_id [id]
    * @return {[GeoJSON]} drainage basin
    */
    get_basin: function(feature, callback) {
        var pp_id = feature.getProperties().ppt_ID;
        app.map.selectedFeature = feature;
        return $.ajax({
            url: '/ucsrb/get_basin',
            data: {
                pourPoint: pp_id,
            },
            dataType: 'json',
            success: function(response) {
                app.state.setFocusArea = response;
                callback(feature, response.geojson);
                return response;
            },
            error: function(response, status) {
                console.log(`%cfail @ get basin: %o`, 'color: red', response);
                // we don't have the ppt basins yet, just get a HUC12 for now.
                app.request.get_focus_area_at(app.map.selectedFeature, 'HUC12', function(feature, hucFeat) {
                    vectors = (new ol.format.GeoJSON()).readFeatures(hucFeat.geojson, {
                        dataProjection: 'EPSG:3857',
                        featureProjection: 'EPSG:3857'
                    });
                    // set property id with hucFeat.id
                    vector = vectors[0].getGeometry();
                    vector.set('layer', 'huc12_3857');
                    vector.set('HUC_12', hucFeat.id.toString());
                    app.request.get_focus_area(vector, 'HUC12', callback);
                });
                return status;
            }
        })
    },
    saveDrawing: function(draw_name, draw_desc) {
        var drawFeatures = app.map.draw.source.getFeatures();
        var geojsonFormat = new ol.format.GeoJSON();
        var featureJson = geojsonFormat.writeFeatures(drawFeatures);

        return $.ajax({
            url: '/ucsrb/save_drawing',
            data: {
                drawing: featureJson,
                // TODO: Set name/description with form
                name: draw_name,
                description: draw_desc
            },
            dataType: 'json',
            method: 'POST',
            success: function(response) {
                app.map.draw.disable();
                app.nav.hideSave();
                if (app.state.nav !== 'short') {
                    app.state.navHeight = 'short';
                    app.state.setStep = 'results'; // go to results
                }
                var vectors = (new ol.format.GeoJSON()).readFeatures(response.geojson, {
                    dataProjection: 'EPSG:3857',
                    featureProjection: 'EPSG:3857'
                });
                // Remove drawing from layer
                var draw_source = app.map.layer.draw.layer.getSource();
                draw_source.removeFeature(draw_source.getFeatures()[0]);
                app.map.addScenario(vectors);
                app.panel.results.init('ucsrb_treatmentscenario_' + response.id);
                app.resultsInit('ucsrb_treatmentscenario_' + response.id);
                app.state.scenarioId = response.id;
                app.state.setStep = 'results';
            },
            error: function(response, status) {
                console.log(`%cfail @ save drawing: %o`, 'color: red', response);
                alert(response.responseJSON.error_msg);
                app.panel.draw.finishDrawing();
            }
        })
    },
    filter_results: function(pourpoint) {
        $.ajax({
            url: "/api/filter_results",
            data: {
                ppid: pourpoint
            },
        })
    },
    saveIntermediateScenario: function(data) {
        $.ajax({
            url: '/scenario/treatmentscenario/save',
            type: 'POST',
            data: data,
            dataType: 'json',
            success: function(response, status) {
                return status;
            },
            error: function(response, status) {
                console.log(`%cfailed save state: %o`, 'color: red', response);
                return status;
            }
        })
    },
    saveState: function() {
        $.ajax({
            url: '/scenario/treatmentscenario/save',
            type: 'POST',
            data: app.saveState,
            dataType: 'json',
            success: function(response, status) {
                return status;
            },
            error: function(response, status) {
                console.log(`%cfail @ save state: %o`, 'color: red', response);
                return status;
            }
        })
    },
    deleteScenario: function(id) {
        return $.ajax({
            url: `/scenario/delete_design/ucsrb_treatmentscenario_${id}/`,
            type: 'POST',
            data: {
                uid: id
            },
            success: function(response, status) {
                return status;
            },
            error: function(response, status) {
                console.log(`%failed to deleted: %o`, 'color: red', response);
                return status;
            }
        })
    }
}
