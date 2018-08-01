
var madrona = {
    onShow: function(callback) { callback(); },
    resetState: function() {
        app.state.setStep = 'reset'; // starts app steps for nav, panel, and instructions
        app.viewModel.scenarios.reset({cancel: true});
        app.state.setStep = 0; // go back to step zero
    },
    setupForm: function($form) {
        //var submitted = false;

        // $form.find('.btn-submit').hide();

        $form.find('label').each(function (i, label) {
            if ($(label).find('input[type="checkbox"]').length) {
                $(label).addClass('checkbox');
            }
        });

        $form.closest('.panel').on('click', '.cancel_button', function(e) {
            madrona.resetState();
        });

        $form.closest('.panel').on('click', '.submit_button', function(e) {
            e.preventDefault();
            var name = $('#id_name').val();
            if ($.trim(name) === "") {
                $('#invalid-name-message').show();
                return false;
            }
            //submitted = true;
            submitForm($form);
        });

        //no longer needed...? (if it was going here it meant there was a problem)
        /*
        $form.submit( function() {
            var name = $('#id_name').val();
            if ($.trim(name) === "") {
                $('#invalid-name-message').show();
                return false;
            }
            if (!submitted) {
                submitForm($form);
            }
        });
        */
        submitForm = function($form) {
            // var $form = $(this).closest('.panel').find('form'),
            var url = $form.attr('action'),
                // $bar = $form.closest('.tab-pane').find('.bar'),
                data = new FormData();
                // barTimer;

            //progress bar
            // barTimer = setInterval(function () {
            //     var width = parseInt($bar.css('width').replace('px', ''), 10) + 5,
            //         barWidth = parseInt($bar.parent().css('width').replace('px',''), 10);
            //
            //     if (width < barWidth) {
            //         $bar.css('width', width + "px");
            //     } else {
            //         clearInterval(barTimer);
            //     }
            // }, 500);

            app.checkboxes = {};
            $form.find('input,select,textarea').each( function(index, input) {
                var $input = $(input);
                if ($input.attr('type') === 'checkbox') {
                    if ($input[0].checked) {
                      if ($input.attr('name').indexOf('checkboxes') >= 0) {
                        if ($input.attr('name') in app.checkboxes) {
                          app.checkboxes[$input.attr('name')].push($input.attr('value'));
                        } else {
                          app.checkboxes[$input.attr('name')] = [$input.attr('value')];
                        }
                      } else {
                        data.append($input.attr('name'), 'True');
                      }
                    } else {
                        data.append($input.attr('name'), 'False');
                    }
                } else {
                    if ($input.attr('type') == 'file') {
                        $.each($input[0].files, function(i, file) {
                            data.append('file-'+i, file);
                        });
                    } else {
                        data.append($input.attr('name'), $input.val());
                    }
                }
            });
            var checkboxList = Object.keys(app.checkboxes);
            for (var i = 0; i < checkboxList.length; i++) {
              data.append(checkboxList[i], app.checkboxes[checkboxList[i]]);
            }

            app.viewModel.scenarios.scenarioForm(false);
            app.viewModel.scenarios.loadingMessage("Creating Design");
            app.loadingAnimation.show();

            $.ajax({
                url: url,
                data: data,
                cache: false,
                contentType: false,
                processData: false,
                type: 'POST',
                traditional: true,
                dataType: 'json',
                success: function(result) {
                    app.loadingAnimation.hide();
                    app.state.setStep = 'result'; // go to results
                    app.resultsInit(result['X-Madrona-Show']);
                    app.viewModel.scenarios.addScenarioToMap(null, {uid: result['X-Madrona-Show']});
                    app.viewModel.scenarios.loadingMessage(false);
                    // clearInterval(barTimer);
                    // app.viewModel.scenarios.loadCollectionsFromServer();
                    console.log(`%c form submitted: %o`, 'color: green;', result);
                },
                error: function(result) {
                    app.loadingAnimation.hide();
                    app.viewModel.scenarios.loadingMessage(null);
                    // clearInterval(barTimer);
                    if (result.status === 400) {
                        $('#'+app.viewModel.currentTocId()+'-scenario-form > div').append(result.responseText);
                        app.viewModel.scenarios.scenarioForm(true);
                    } else {
                        app.viewModel.scenarios.errorMessage(result.responseText.split('\n\n')[0]);
                    }
                    console.log(`%c form not submitted; %o`, 'color: salmon;', result);
                }
            });
        };

    }
}; // end madrona init


function scenarioFormModel(options) {
    var self = this;
    self.focus_area = ko.observable(false);
    self.private_own = ko.observable(false);
    self.pub_priv_own = ko.observable(false);
    // self.pub_priv_own_input = ko.observable(false);
    self.lsr_percent = ko.observable(false);
    self.has_critical_habitat = ko.observable(false);
    self.percent_roadless = ko.observable(false);
    self.road_distance = ko.observable(false);
    // self.road_distance_max = ko.observable(false);
    self.percent_wetland = ko.observable(false);
    self.percent_riparian = ko.observable(false);
    self.slope = ko.observable(false);
    self.percent_fractional_coverage = ko.observable(false);
    self.percent_high_fire_risk_area = ko.observable(false);
    self.landform_type = ko.observable(false);
    self.landform_type_checkboxes_include_0 = ko.observable(true); //north
    self.landform_type_checkboxes_include_1 = ko.observable(true); //south
    self.landform_type_checkboxes_include_2 = ko.observable(true); //ridgetop
    self.landform_type_checkboxes_include_3 = ko.observable(true); //floors
    self.landform_type_checkboxes_include_4 = ko.observable(true); //east/west

    self.lastChange = (new Date()).getTime();

    try {
      mapSettings;
    } catch(err) {
      mapSettings = {};
    }

    if (mapSettings.getInitFilterResultsLayer) {
      self.updatedFilterResultsLayer = mapSettings.getInitFilterResultsLayer();
    } else {
      //old OL2 code - will break and let us know when we haven't overridden it.
      mapSettings.defaultStyle = new OpenLayers.Style({
          //display: 'none'
          fillColor: '#5c7352',
          fillOpacity: .5,
          strokeColor: '#e6e7e8',
          strokeOpacity: .9,
          strokeWidth: 1,
          strokeDash: [2,4],
          zIndex: 1,
      });
      var styleMap = new OpenLayers.StyleMap( {
          'default': mapSettings.defaultStyle
      });
      self.updatedFilterResultsLayer = new OpenLayers.Layer.Vector('Current Filter Results', {
          projection: new OpenLayers.Projection('EPSG:3857'),
          displayInLayerSwitcher: false,
          styleMap: styleMap
      });
    }

    app.map.addLayer(self.updatedFilterResultsLayer);

    /** Toggle an input div. */
    self.toggleParameter = function(param) {
        var param_bool = self[param];
        var param_element = $('#id_' + param);
        var param_widget = $('#' + param + '_widget');

        if (param_bool()) {
            param_bool(false);
            param_element.removeAttr('checked');
            param_widget.css('display', 'none');
            self.removeFilter(param);
        } else {
            if (param_widget) {
                var input = param_widget.find('input');
                var range = input.attr('range');
                if (range) {
                    param_widget.find('.slider').first().slider('option', 'range', 'max');
                }
            }
            param_bool(true);
            param_element.attr('checked', 'checked');
            param_widget.css('display', 'block');
            self.updateFilters(param);
        }

        self.updateFilterCount(param);
    };

    self.filters = {};

    // Toggle Data Layers and Layer Info

    self.toggleLayerInfo = function(layerID) {
        var layer = app.viewModel.getLayerById(layerID);
        if (layer) {
            if ( layer.infoActive() ) {
                layer.hideDescription(layer);
            } else {
                layer.showDescription(layer);
            }
            return true;
        }
        return false;
    };

    self.isLayerInfoActive = function(layerID) {
        var layer = app.viewModel.getLayerById(layerID);
        if (layer) {
            return layer.infoActive();
        }
        return false;
    };

    self.isLayerActive = function(layerID) {
        var layer = app.viewModel.getLayerById(layerID);
        if (layer) {
            return layer.active();
        }
        return false;
    };

    self.isLayerVisible = function(layerID) {
        var layer = app.viewModel.getLayerById(layerID);
        if (layer) {
            return layer.visible();
        }
        return false;
    };

    self.toggleLayer = function(layerID) {
        var layer = app.viewModel.getLayerById(layerID);
        if (layer) {
            if ( layer.active() ) {
                layer.deactivateLayer();
            } else {
                layer.activateLayer();
            }
            return true;
        }
        return false;
    };

    // Updating Dynamic Display

    self.gridCellsRemaining = ko.observable('...');
    self.filterNotesExist = ko.observable(false);
    self.filterNotesMessage = ko.observable('');
    self.showingFilteringResults = ko.observable(true);
    self.inputsHaveChanged = ko.observable(true);
    self.showButtonSpinner = ko.observable(false);
    self.currentCountRequest = ko.observable(false);
    self.currentGridRequest = ko.observable(false);
    self.lastChange = (new Date()).getTime();

    self.showFilteringResults = function() {
        if (self.showingFilteringResults()) {
            self.stopShowingFilteringResults();
        } else {
            self.showingFilteringResults(true);
            self.updatedFilterResultsLayer.setVisibility(true);
            if (self.inputsHaveChanged()) {
                self.inputsHaveChanged(false);
                self.getUpdatedFilterResults();
            }
        }
    };

    self.stopShowingFilteringResults = function() {
        self.showingFilteringResults(false);
        self.updatedFilterResultsLayer.setVisibility(false);
    };

    self.updateFiltersAndCount = function(param) {
        self.updateFilters(param);
        self.updateFilterCount(param);
    };

    self.updateFilterCount = function(param) {
        if (self.updateTimeout) {
            clearTimeout(self.updateTimeout);
        }
        self.inputsHaveChanged(true);
        if (self.showingFilteringResults()) {
            self.showButtonSpinner(true);
        }
        self.gridCellsRemaining('...');
        self.filterNotesExist(false);
        self.filterNotesMessage('');
        self.updatedFilterResultsLayer.removeAllFeatures();

        self.updateFilterResults();

    };

    self.updateFilterResults = function() {
        if (self.showingFilteringResults()) {
            self.getUpdatedFilterResults();
        } else {
            self.getUpdatedFilterCount();
        }
    };

    self.getUpdatedFilterCount = function() {
        $.ajax({
            url: '/scenario/get_filter_count',
            type: 'GET',
            data: self.filters,
            success: function(data) {
                self.gridCellsRemaining(data);
            },
            error: function(error) {
                console.log('error in getUpdatedFilterCount: ' + error);
            }
        });
    };

    self.getUpdatedFilterResults = function() {
        self.updatedFilterResultsLayer.setVisibility(false);
        self.showButtonSpinner(true);

        (function() {
            var request = $.ajax({
                url: '/scenario/get_filter_results',
                type: 'GET',
                data: self.filters,
                dataType: 'json',
                success: function(data) {
                    if (self.currentGridRequest() === request) {
                        var wkt = data[0].wkt,
                            featureCount = data[0].count,
                            area_m2 = data[0].area_m2;
                            area_acres = data[0].area_acres;
                            if (data[0].notes.length > 0) {
                              self.filterNotesMessage(data[0].notes);
                              self.filterNotesExist(true);
                            }
                        self.updatedFilterResultsLayer.removeAllFeatures();
                        if (featureCount && wkt) {
                            self.updatedFilterResultsLayer.addWKTFeatures(wkt);
                        }
                        self.updatedFilterResultsLayer.setVisibility(true);
                        acres = area_acres;
                        self.gridCellsRemaining(parseInt(acres) + ' acres');

                      if (parseInt(acres) < parseInt(app.map.draw.maxAcres)) {
                          $('.submit_button').removeClass('disabled');
                          $('#scenarios-form .alert').addClass('d-none');
                      } else {
                          if ($('#scenarios-form .alert').length > 0) {
                              $('#scenarios-form .alert').removeClass('d-none');
                          } else {
                              $('#scenarios-form').append(`<div class="alert alert-warning" role="alert">Too large of area. Filter to less than ${app.map.draw.maxAcres} acres.`);
                          }
                      }

                        self.showButtonSpinner(false);
                    }
                },
                error: function(result) {
                    self.showButtonSpinner(false);
                    self.showingFilteringResults(false);
                    console.log('%cerror in getUpdatedFilterResults: %o', 'color: red', result);
                }
            });
            self.currentGridRequest(request);
            var request = request;
        })();
    };

    self.updateFilters = function(param) {
        var min, max, input, checkboxes,
            param_element_min = $('#id_' + param + '_min')[0],
            param_element_max = $('#id_' + param + '_max')[0],
            param_element_input = $('#id_' + param + '_input')[0],
            param_element_checkboxes = $('#id_' + param + '_checkboxes_0')[0];

        if (param_element_min) {
            min = param_element_min.value;
        }
        if (param_element_max) {
            max = param_element_max.value;
        }
        if (param_element_input) {
            input = param_element_input.value;
        }
        if (param_element_checkboxes) {
            checkboxes = [];
            var i = 0;
            while ($('#id_' + param + '_checkboxes_' + i.toString())[0]) {
                var box = $('#id_' + param + '_checkboxes_' + i.toString())[0];
                if (box.checked) {
                    checkboxes.push(box.value);
                }
                i++;
            }
        }
        self.updateFilter(param, min, max, input, checkboxes);
    };

    // TODO: Cleanup needed. This was written to take 5 parameters to explicitly
    //  assign values on function call. Instead, these will all be null and require
    //  jQuery to identify values - this also means strict enforcement of field
    //  names/ids.
    self.updateFilter = function(param, min, max, input, checkboxes) {
        var key;
        self.filters[param] = true;
        var key_object = {
          '_min': min,
          '_max': max,
          '_input': input,
          '_checkboxes': checkboxes
        }
        for (var i = 0; i < Object.keys(key_object).length; i++) {
          suffix = Object.keys(key_object)[i];
          if (suffix == '_checkboxes') {
            field_value = key_object[suffix];
            // Handle directly passed variable for checkboxes
            if (field_value) {
              key = param + suffix;
              self.filters[key] = true;
              for(var j = 0; j < checkboxes.length; j++) {
                  key = param + '_checkboxes_' + checkboxes[j];
                  self.filters[key] = true;
              }
            // Look for existing values in the form iteslf with jQuery
            } else if ($('#id_' + key).length > 0 && $('#id_' + key)[0].checked) {
              self.filters[key] = true;
              var checkboxes = [];
              var j = 0;
              var checkbox_key = key + '_0';
              while ($('id_' + checkbox_key)[0]) {
                var box = $('#id_' + checkbox_key)[0];
                if (box.checked) {
                  // checkboxes.push(box.value);
                  self.filters[checkbox_key] = true;
                }
                j++;
                checkbox_key = key + '_' + j.toString();
              }
            }
          } else {
            // Handle directly passed variable
            field_value = key_object[suffix];
            if (field_value) {
              key = param + suffix;
              self.filters[key] = field_value;
            // Look for existing values in the form iteslf with jQuery
            } else if ($('#id_' + key).length > 0) {
              self.filters[key] = $('#id_' + key).value();
            }
          }
        }
    };

    self.removeFilter = function(key) {
        delete self.filters[key];
        delete self.filters[key+'_min'];
        delete self.filters[key+'_max'];
        delete self.filters[key+'_input'];
        if (self.filters.hasOwnProperty(key+'_checkboxes')) {
            delete self.filters[key+'_checkboxes'];
            var filter_keys = Object.keys(self.filters);
            var box_keys = [];
            for(var counter = 0; counter < filter_keys.length; counter++) {
                if (filter_keys[counter].indexOf(key+'_checkboxes_') > -1) {
                    box_keys.push(filter_keys[counter]);
                }
            }
            for(var i = 0; i < box_keys.length; i++) {
                delete self.filters[box_keys[i]];
            }
        }
    };

    self.updateDesignScrollBar = function() {
        var designsWizardScrollpane = $('#wind-design-form').data('jsp');
        if (designsWizardScrollpane === undefined) {
            $('#wind-design-form').jScrollPane();
        } else {
            setTimeout(function() {designsWizardScrollpane.reinitialise();},100);
        }
    };

    return self;
} // end scenarioFormModel


function scenarioModel(options) {
    var self = this;

    self.id = options.uid || null;
    self.uid = options.uid || null;
    self.name = options.name;
    self.display_name = options.display_name?options.display_name:self.name;
    self.collection = options.collection;
    self.featureAttributionName = self.name;
    self.description = options.description;
    self.shared = ko.observable();
    self.sharedByName = options.sharedByName || null;
    self.sharedByUsername = options.sharedByUsername;
    if (self.sharedByName && $.trim(self.sharedByName) !== '') {
        self.sharedByWho = self.sharedByName + ' (' + self.sharedByUsername + ')';
    } else {
        self.sharedByWho = self.sharedByUsername;
    }
    self.sharedBy = ko.observable();
    if (options.shared) {
        self.shared(true);
        self.sharedBy('Shared by ' + self.sharedByWho);
    } else {
        self.shared(false);
        self.sharedBy(false);
    }
    self.selectedGroups = ko.observableArray();
    self.sharedGroupsList = [];
    if (options.sharingGroups && options.sharingGroups.length) {
        self.selectedGroups(options.sharingGroups);
    }
    self.sharedWith = ko.observable();
    self.updateSharedWith = function() {
        if (self.selectedGroups().length) {
            var groupNames = "Shared with " + self.selectedGroups()[0];
            for(var i=1; i<self.selectedGroups().length; i+=1) {
                groupNames += ", " + self.selectedGroups()[i];
            }
            self.sharedWith(groupNames);
        }
    };
    self.updateSharedWith();
    self.selectedGroups.subscribe( function() {
        self.updateSharedWith();
    });
    self.temporarilySelectedGroups = ko.observableArray();

    self.selectedScenarios = ko.observableArray();
    self.temporarilySelectedScenarios = ko.observableArray();

    self.isLayerModel = ko.observable(false);

    self.attributes = ko.observable([]);
    self.scenarioAttributes = ko.observable(options.attributes ? options.attributes.attributes : []);

    self.showingLayerAttribution = ko.observable(false);
    self.toggleLayerAttribution = function() {
        var layerID = '#' + app.viewModel.convertToSlug(self.name);
        if ( self.showingLayerAttribution() ) {
            self.showingLayerAttribution(false);
            $(layerID).css('display', 'none');
        } else {
            self.showingLayerAttribution(true);
            $(layerID).css('display', 'block');
        }
        //update scrollbar
        app.viewModel.updateAggregatedAttributesOverlayScrollbar();
    };

    //self.overview = self.description || 'no description was provided';
    self.constructInfoText = function() {
        var attrs = self.scenarioAttributes(),
            output = '';

        if (attrs){
            for (var i=0; i< attrs.length; i++) {
                output += attrs[i].title + ': ' + attrs[i].data + '\n';
            }
        }
        return output;
    };
    self.overview = self.constructInfoText();

    self.scenarioReportValues = options.attributes ? options.attributes.report_values : [];

    self.features = options.features;

    self.active = ko.observable(false);
    self.visible = ko.observable(false);
    self.defaultOpacity = options.opacity || 0.8;
    self.opacity = ko.observable(self.defaultOpacity);
    self.type = 'Vector';

    self.opacity.subscribe( function(newOpacity) {
        if ( self.hasOwnProperty('layer') ) {
            self.layer.styleMap.styles['default'].defaultStyle.strokeOpacity = newOpacity;
            self.layer.styleMap.styles['default'].defaultStyle.fillOpacity = newOpacity;
            self.layer.redraw();
        }
    });

    self.toggleActive = function(self, event) {
        var scenario = this;

        // start saving restore state again and remove restore state message from map view
        app.saveStateMode = true;
        app.viewModel.error(null);
        //app.viewModel.unloadedDesigns = [];

        //app.viewModel.activeLayer(layer);
        if (scenario.active()) { // if layer is active, then deactivate
            scenario.deactivateLayer();
        } else { // otherwise layer is not currently active, so activate
            scenario.activateLayer();
            //app.viewModel.scenarios.addScenarioToMap(scenario);
        }
    };

    self.activateLayer = function() {
        var scenario = this;
        app.viewModel.scenarios.addScenarioToMap(scenario);
    };

    self.deactivateLayer = function() {
        var scenario = this;

        scenario.active(false);
        scenario.visible(false);

        scenario.opacity(scenario.defaultOpacity);
        app.setLayerVisibility(scenario, false);
        app.viewModel.activeLayers.remove(scenario);

        app.viewModel.removeFromAggregatedAttributes(scenario.name);

    };

    self.editScenario = function() {
        var scenario = this;
        return $.ajax({
            url: '/features/scenario/' + scenario.uid + '/form/',
            success: function(data) {
                app.viewModel.scenarios.scenarioForm(true);
                $('#'+app.viewModel.currentTocId()+'-scenario-form > div').html(data);
                app.viewModel.scenarios.scenarioFormModel = new scenarioFormModel();
                var model = app.viewModel.scenarios.scenarioFormModel;

                ko.applyBindings(model, document.getElementById(app.viewModel.currentTocId()+'-scenario-form').children[0]);

                var parameters = [
                    'species',
                    'lifestage',
                    'mean_fthm',
                    'hsall_m2',
                    // 'hsall1_m2',
                    // 'hsall2_m2',
                    // 'hsall3_m2',
                    // 'hsall4_m2',
                    'hpc_est_m2',
                    'hpc_klp_m2',
                    'hpc_rck_m2',
                    'hpc_sgr_m2',
                    'sft_sub_m2',
                    'mix_sub_m2',
                    'hrd_sub_m2',
                    'rck_sub_m2',
                    'cnt_cs',
                    'cnt_penn'
                ];

                for (var i = 0; i < parameters.length; i++) {
                    var id = '#id_' + parameters[i];

                    if ($(id).is(':checked')) {
                        model.toggleParameter(parameters[i]);
                    }
                }

                app.viewModel.scenarios.loadScenariosFromServer();
                app.viewModel.scenarios.updateDesignsScrollBar();
                window.dispatchEvent(new Event('resize'));

                // model.updateFiltersAndLeaseBlocks();
            },
            error: function (result) {
                console.log('error in scenarios.js: editScenario');
            }
        });
    };

    self.createCopyScenario = function() {
        var scenario = this;

        //create a copy of this shape to be owned by the user
        $.ajax({
            url: '/scenario/copy_design/' + scenario.uid + '/',
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                //app.viewModel.scenarios.loadSelectionsFromServer();
                app.viewModel.scenarios.addScenarioToMap(null, {uid: data[0].uid});
                app.viewModel.scenarios.loadScenariosFromServer();
                app.viewModel.scenarios.updateDesignsScrollBar();
            },
            error: function (result) {
                console.log('error in scenarios.js: createCopyScenario');
            }
        });
    };

    self.deleteScenario = function() {
        var scenario = this;

        //first deactivate the layer
        scenario.deactivateLayer();

        //remove from activeLayers
        app.viewModel.activeLayers.remove(scenario);
        //remove from app.map
        if (scenario.layer) {
            app.map.removeLayer(scenario.layer);
        }
        //remove from scenarioList
        app.viewModel.scenarios.scenarioList.remove(scenario);
        //update scrollbar
        app.viewModel.scenarios.updateDesignsScrollBar();

        //remove from server-side db (this should provide error message to the user on fail)
        $.ajax({
            url: '/scenario/delete_design/' + scenario.uid + '/',
            type: 'POST',
            success: function(result){
              app.viewModel.scenarios.loadScenariosFromServer();
              app.viewModel.scenarios.loadCollectionsFromServer();
            },
            error: function(result) {
                console.log('error in scenarios.js: deleteScenario');
            }
        });
    };

    self.visible = ko.observable(false);

    // bound to click handler for layer visibility switching in Active panel
    self.toggleVisible = function() {
        var scenario = this;

        if (scenario.visible()) { //make invisible
            scenario.visible(false);
            app.setLayerVisibility(scenario, false);

            app.viewModel.removeFromAggregatedAttributes(scenario.name);

        } else { //make visible
            scenario.visible(true);
            app.setLayerVisibility(scenario, true);
        }
    };

    // is description active
    self.infoActive = ko.observable(false);
    app.viewModel.showOverview.subscribe( function() {
        if ( app.viewModel.showOverview() === false ) {
            self.infoActive(false);
        } else {
          console.log('show overview');
          app.viewModel.scenarios.getAttributes(self.uid);
        }
    });

    // display descriptive text below the map
    self.toggleDescription = function(scenario) {
        if ( ! scenario.infoActive() ) {
            self.showDescription(scenario);
        } else {
            self.hideDescription(scenario);
        }
    };

    self.showDescription = function(scenario) {
        app.viewModel.showOverview(false);
        app.viewModel.activeInfoSublayer(false);
        app.viewModel.activeInfoLayer(scenario);
        self.infoActive(true);
        $('#overview-overlay').height(186);
        app.viewModel.showOverview(true);
        app.viewModel.updateCustomScrollbar('#overview-overlay-text');
        // app.viewModel.hideMapAttribution();
        app.viewModel.closeAttribution();
    };

    self.hideDescription = function(scenario) {
        app.viewModel.showOverview(false);
        app.viewModel.activeInfoSublayer(false);
        app.viewModel.showMapAttribution();
    };

    return self;
} // end scenarioModel

/*
--Scenarios Model
-- This model manages a vast majority of the 'designs' tab.
-- These functions are for manipulating scenarios, drawings, and collections.
-- This is where a good share of the business logic for related modals is
-- contained as well.

-- This may have also been a bad design decision trying to treat collections
-- with the name 'sceanarios' even though there's a viewModel for collections
-- already in drawings.js.
*/
function scenariosModel(options) {
    var self = this;

    self.scenarioList = ko.observableArray();
    self.scenarioForm = ko.observable(false);

    self.drawingCollections = [];
    self.drawingListCollections = ko.observableArray([]);
    self.drawingList = ko.observableArray();
    self.drawingForm = ko.observable(false);
    self.drawingsExist = ko.observable();

    self.collectionList = ko.observableArray();
    self.collectionForm = ko.observable(false);

    self.reportsVisible = ko.observable(false);

    self.filterLayer = ko.observable(false);

    self.filterLayer.subscribe( function() {
        app.viewModel.updateAttributeLayers();
    });

    self.scenarioLeaseBlocksLayerName = 'Selected OCS Blocks';

    // loading message for showing spinner
    // false for normal operation
    self.loadingMessage = ko.observable(false);
    self.errorMessage = ko.observable(false);

    self.sharingGroups = ko.observableArray();
    self.hasSharingGroups = ko.observable(false);

    self.sharingLayer = ko.observable();
    self.showSharingModal = function(scenario) {
        self.sharingLayer(scenario);
        self.sharingLayer().temporarilySelectedGroups(self.sharingLayer().selectedGroups().slice(0));
        $('#share-modal').modal('show');
    };

    self.groupMembers = function(groupName) {
        var memberList = "";
        for (var i=0; i<self.sharingGroups().length; i++) {
            var group = self.sharingGroups()[i];
            if (group.group_name === groupName) {
                for (var m=0; m<group.members.length; m++) {
                    var member = group.members[m];
                    memberList += member + '<br>';
                }
            }
        }
        return memberList;
    };

    self.toggleGroup = function(obj) {
        var groupName = obj.group_name,
            indexOf = self.sharingLayer().temporarilySelectedGroups.indexOf(groupName);
        if ( indexOf === -1 ) {  //add group to list
            self.sharingLayer().temporarilySelectedGroups.push(groupName);
        } else { //remove group from list
            self.sharingLayer().temporarilySelectedGroups.splice(indexOf, 1);
        }
    };

    self.initSharingModal = function() {
        for (var i=0; i<self.sharingGroups().length; i++) {
            var groupID = '#' + self.sharingGroups()[i].group_slug;
            $(groupID).collapse( { toggle: false } );
        }
    };

    //TODO:  Fix the problem in which the first group toggled open will not toggle open again, once it's closed
    self.lastMembersClickTime = 0;
    self.toggleGroupMembers = function(obj, e) {
        var groupName = obj.group_name,
            groupID = '#' + obj.group_slug,
            clickTime = new Date().getTime();
        if (clickTime - self.lastMembersClickTime > 800) {
            self.lastMembersClickTime = clickTime;
            if ( ! $(groupID).hasClass('in') ) {  //toggle on and add group to list
                $(groupID).css("display", "none"); //allows the fade effect to display as expected
                if ( $.browser.msie ) {
                    $(groupID).fadeIn(0, function() {});
                } else {
                    $(groupID).fadeIn('slow', function() {});
                }
                $(groupID).collapse('show');
            } else { //toggle off and remove group from list
                if ( $.browser.msie ) {
                    $(groupID).fadeOut(0, function() {});
                } else {
                    $(groupID).fadeOut('slow', function() {});
                }
                $(groupID).collapse('hide');
                //set .modal-body background to eliminate residue that appears when the last Group is opened and then closed?
            }
            setTimeout(function() { self.updateSharingScrollBar(groupID); }, 300);
        }
    };

    self.groupIsSelected = function(groupName) {
        if (self.sharingLayer()) {
            var indexOf = self.sharingLayer().temporarilySelectedGroups.indexOf(groupName);
            return indexOf !== -1;
        }
        return false;
    };



    self.hasAssociatedScenarios = ko.observable(false);

    self.associatedDrawing = ko.observable();
    self.showAssociationModal = function(drawing){
        self.associatedDrawing(drawing);
        self.associatedDrawing().temporarilySelectedScenarios(self.associatedDrawing().selectedScenarios().slice(0));
        $('#draw-scenario-associate-modal').modal('show');
    };

    self.toggleScenario = function(obj) {
      var scenarioId = obj.uid;
      if (self.associatedDrawing()) {
          var indexOf = self.associatedDrawing().temporarilySelectedScenarios.indexOf(scenarioId);
      } else {
          var indexOf = -1;
      }
      if ( indexOf === -1 ) {  //add group to list
          self.associatedDrawing().temporarilySelectedScenarios.push(scenarioId);
      } else { //remove group from list
          self.associatedDrawing().temporarilySelectedScenarios.splice(indexOf, 1);
      }
    }

    self.scenarioIsSelected = function(scenarioId) {
        if(self.associatedDrawing()) {
            var indexOf = self.associatedDrawing().temporarilySelectedScenarios.indexOf(scenarioId);
            return indexOf !== -1;
        }
        return false;
    }

    self.showImportRequirementsModal = function(){
      $('#import-guidelines-modal').modal('show');
    };

    self.comparisonCollection = ko.observable();
    self.showComparisonModal = function(collection){
        self.comparisonCollection(collection);
        self.comparisonCollection().temporarilySelectedScenarios(self.comparisonCollection().selectedScenarios().slice(0));
        $('#collection-compare-modal').modal('show');
    };

    self.toggleCompareScenario = function(obj) {
      var scenarioId = obj.uid;
      if (self.comparisonCollection()) {
          var indexOf = self.comparisonCollection().temporarilySelectedScenarios.indexOf(scenarioId);
      } else {
          var indexOf = -1;
      }
      if ( indexOf === -1 ) {  //add group to list
          self.comparisonCollection().temporarilySelectedScenarios.push(scenarioId);
      } else { //remove group from list
          self.comparisonCollection().temporarilySelectedScenarios.splice(indexOf, 1);
      }
    }

    self.obsArrayValue = function(obsarray) {
      return JSON.parse(ko.toJSON(obsarray));
    }

    self.compareScenarioIsSelected = function(scenarioId) {
        if(self.comparisonCollection()) {
            var indexOf = self.comparisonCollection().temporarilySelectedScenarios.indexOf(scenarioId);
            return indexOf !== -1;
        }
        return false;
    }

    /*
        Populate Scenario Comparison Report Modal
    */
    self.originalComparisonReport = ko.observableArray();
    self.comparisonReport = ko.observableArray();
    self.comparisonReportCollections = ko.observableArray();
    self.comparisonReportValues = ko.observableArray();
    self.comparisonDownloadLink = ko.observable();
    self.showComparisonReportModal = function(array,data,download_link) {
      self.comparisonReportCollections(Object.getOwnPropertyNames(data));
      self.comparisonReportValues(array);
      self.comparisonDownloadLink(download_link);
      var data_array = [];
      for (var i=0; i < self.comparisonReportValues().length; i++) {
        var key = self.comparisonReportValues()[i];
        var row = [key];
        for (var j=0; j < self.comparisonReportCollections().length; j++) {
          collection_name = self.comparisonReportCollections()[j];
          collection_object = data[collection_name]
          row.push(collection_object[key]);
        }
        data_array.push(row);
      }
      self.originalComparisonReport(data_array);
      self.comparisonReport(self.obsArrayValue(self.originalComparisonReport));
      $('#compare-report-modal').modal('show');
    };

    self.setComparisonReportBaseline = function(baselineIndex) {
      if (baselineIndex == 0) {
        self.comparisonReport([]);
        self.comparisonReport(self.obsArrayValue(self.originalComparisonReport));
      } else {
        reportValues = self.obsArrayValue(self.originalComparisonReport);
        //Loop through fields
        for(var i=0; i < reportValues.length; i++) {
          if (
            typeof(reportValues[i][1]) == 'object' &&
            reportValues[i][1] != null &&
            reportValues[i][1].hasOwnProperty('values') &&
            reportValues[i][1].hasOwnProperty('text') &&
            typeof(reportValues[i][1]['text']) == 'object'
          ){
            //for values in each field (discluding field name at 0)
            for (var j=1; j<reportValues[i].length; j++) {
              blValues = reportValues[i][baselineIndex]['values'];
              //change non-baseline displayed values
              if (j!=baselineIndex){
                for (k=0; k < reportValues[i][j]['values'].length; k++){
                  old_val = reportValues[i][j]['values'][k];
                  //Determine type of values: int or float
                  if (old_val%1 == 0) {
                    //calculate difference (absolute for now, maybe % later)
                    diff_val = parseInt(old_val) - parseInt(blValues[k]);
                  } else{
                    diff_val = parseFloat(old_val) - parseFloat(blValues[k])
                    // reportValues[i][j]['values'][k] = ().toString();
                  }
                  if (diff_val > 0) {
                    diff_val = "+" + diff_val.toString();
                  } else {
                    diff_val = diff_val.toString();
                  }
                  reportValues[i][j]['values'][k] = diff_val;
                  //assemble new label - assumes text & values will alternate
                  if (reportValues[i][j]['values'].length >= reportValues[i][j]['text'].length) {
                    big_list = reportValues[i][j]['values'];
                    small_list = reportValues[i][j]['text'];
                  } else {
                    big_list = reportValues[i][j]['text'];
                    small_list = reportValues[i][j]['values'];
                  }
                  label_list = []
                  for (l = 0; l < big_list.length; l++){
                    label_list.push(big_list[l]);
                    if (l < small_list.length){
                      label_list.push(small_list[l]);
                    }
                  }
                  reportValues[i][j]['label'] = label_list.join(' ');
                }
              }
            }
          }
        }
        self.comparisonReport([]);
        self.comparisonReport(reportValues);
      }
    };

    self.zoomToScenario = function(scenario) {
        if (scenario.layer) {
            var layer = scenario.layer;
            if (!scenario.active()) {
                scenario.activateLayer();
            }
            app.map.zoomToExtent(layer.getDataExtent());
            if (scenario.uid.indexOf('drawing') !== -1) {
                app.map.zoomOut();
                app.map.zoomOut();
            }
        } else {
            self.addScenarioToMap(scenario, {zoomTo: true});
        }
    };

    self.updateSharingScrollBar = function(groupID) {
        var sharingScrollpane = $('#sharing-groups').data('jsp');
        if (sharingScrollpane === undefined) {
            $('#sharing-groups').jScrollPane( {animateScroll: true});
        } else {
            sharingScrollpane.reinitialise();
            var groupPosition = $(groupID).position().top,
                containerPosition = $('#sharing-groups .jspPane').position().top,
                actualPosition = groupPosition + containerPosition;
            //console.log('group position = ' + groupPosition);
            //console.log('container position = ' + containerPosition);
            //console.log('actual position = ' + actualPosition);
            if (actualPosition > 140) {
                //console.log('scroll to ' + (groupPosition-120));
                sharingScrollpane.scrollToY(groupPosition-120);
            }

        }
    };


    // scenariosLoaded will be set to true after they have been loaded
    self.scenariosLoaded = false;

    self.isScenariosOpen = ko.observable(false);
    self.toggleScenariosOpen = function(force) {
        // ensure designs tab is activated

        if (force.hasOwnProperty('tocid')){
            $('#'+force.tocid+'-designsTab').tab('show');
        }

        if (force === 'open') {
            self.isScenariosOpen(true);
        } else if (force === 'close') {
            self.isScenariosOpen(false);
        } else {
            if ( self.isScenariosOpen() ) {
                self.isScenariosOpen(false);
            } else {
                self.isScenariosOpen(true);
            }
        }
        self.updateDesignsScrollBar();
    };
    self.isCollectionsOpen = ko.observable(false);
    self.toggleCollectionsOpen = function(force) {
        // ensure designs tab is activated
        if (force.hasOwnProperty('tocid')){
            $('#'+force.tocid+'-designsTab').tab('show');
        }

        if (force === 'open') {
            self.isCollectionsOpen(true);
        } else if (force === 'close') {
            self.isCollectionsOpen(false);
        } else {
            if ( self.isCollectionsOpen() ) {
                self.isCollectionsOpen(false);
            } else {
                self.isCollectionsOpen(true);
            }
        }
        self.updateDesignsScrollBar();
    };
    self.isDrawingsOpen = ko.observable(false);
    self.toggleDrawingsOpen = function(force) {
        // ensure designs tab is activated
        if (force.hasOwnProperty('tocid')){
            $('#'+force.tocid+'-designsTab').tab('show');
        }

        if (force === 'open') {
            self.isDrawingsOpen(true);
        } else if (force === 'close') {
            self.isDrawingsOpen(false);
        } else {
            if ( self.isDrawingsOpen() ) {
                self.isDrawingsOpen(false);
            } else {
                self.isDrawingsOpen(true);
            }
        }
        self.updateDesignsScrollBar();
    };

    self.updateDesignsScrollBar = function() {
        var designsScrollpane = $('#'+app.viewModel.currentTocId()+'-designs-accordion').data('jsp');
        // if (designsScrollpane === undefined) {
        //     $('#'+app.viewModel.currentTocId()+'-designs-accordion').jScrollPane();
        // } else {
        //     designsScrollpane.reinitialise();
        // }
    };

    //restores state of Designs tab to the initial list of designs
    self.reset = function (obj) {
        self.loadingMessage(false);
        self.errorMessage(false);

        //clean up scenario form
        if (self.scenarioForm() || self.scenarioFormModel) {
            app.map.removeLayer(self.scenarioFormModel.updatedFilterResultsLayer);
            self.removeScenarioForm();
        }

        //clean up drawing form
        if (self.drawingForm() || self.drawingFormModel) {
            self.removeDrawingForm(obj);
        }

        //clear up collection form
        if (self.collectionForm() || self.collectionFormModel) {
            self.removeCollectionForm();
        }

        //remove the key/value pair from aggregatedAttributes
        app.viewModel.removeFromAggregatedAttributes(self.filterLayer().name);
        app.viewModel.updateAttributeLayers();

        self.updateDesignsScrollBar();
    };

    self.removeDrawingForm = function(obj) {
        self.drawingFormModel.cleanUp();
        self.drawingForm(false);
        var drawingForm = document.getElementById(app.viewModel.currentTocId()+'-drawing-form').children[0];
        $(drawingForm).empty();
        ko.cleanNode(drawingForm);
        //in case of canceled edit
        if ( obj && obj.cancel && self.drawingFormModel.originalDrawing ) {
            self.drawingFormModel.originalDrawing.deactivateLayer();
            self.drawingFormModel.originalDrawing.activateLayer();
        }
        delete self.drawingFormModel;
    };

    self.removeScenarioForm = function() {
        self.scenarioForm(false);
        try {
          var scenarioForm = document.getElementById(app.viewModel.currentTocId()+'-scenario-form').children[0];
        } catch (err) {
          //RDH 1/10/2018 - this may work for demo. What to do to repopulate the form?
          // var scenarioForm = document.getElementById('scenario_form').children[0];
          // DLP 3.16.18 - removing all children
          var scenarioForm = document.getElementById('scenario_form');
        }
        $(scenarioForm).empty();
        ko.cleanNode(scenarioForm);
        delete self.scenarioFormModel;
        delete app.viewModel.scenarios.scenarioFormModel;
        //hide remaining leaseblocks
        if ( self.filterLayer() && app.map.getLayersByName(self.filterLayer().name).length ) {
            app.map.removeLayer(self.filterLayer());
        }
    };

    self.removeCollectionForm = function() {
        self.collectionForm(false);
        var collectionForm = document.getElementById(app.viewModel.currentTocId()+'-scenario-collection-form').children[0];
        $(collectionForm).empty();
        ko.cleanNode(collectionForm);
        delete self.collectionFormModel;
    };

    self.createNewScenario = function(form_url) {
        //hide designs tab by sliding left
        if (!form_url) {
          form_url = '/features/scenario/form/';
        }
        // app.loadingAnimation.show();
        return $.ajax({
            url: form_url,
            success: function(data) {
                self.scenarioForm(true);
                $('#scenario_form').html(data);
                self.scenarioFormModel = new scenarioFormModel();
                app.viewModel.scenarios.scenarioFormModel = self.scenarioFormModel;
                var model = app.viewModel.scenarios.scenarioFormModel;
                app.state.formModel = model;
                try {
                  var form_id = app.viewModel.currentTocId()+'-scenario-form';
                  ko.applyBindings(self.scenarioFormModel, document.getElementById(form_id).children[0]);
                } catch (err) {
                  var form_id = 'scenario_form';
                  ko.applyBindings(app.viewModel.scenarios.scenarioFormModel, document.getElementById(form_id).children[0]);
                }
                if ( ! self.filterLayer() && app.viewModel.modernBrowser() ) {
                    self.loadLeaseblockLayer();
                }
                // app.loadingAnimation.hide();
                // window.dispatchEvent(new Event('resize'));
            },
            error: function (result) {
                console.log('failure at scenarios.js "createNewScenario".');
                // app.loadingAnimation.hide();
            }
        });
    };

    self.createPolygonDesign = function() {
        return $.ajax({
            url: '/features/aoi/form/',
            success: function(data) {
                app.viewModel.scenarios.drawingForm(true);
                $('#'+app.viewModel.currentTocId()+'-drawing-form > .drawing-form').html(data);
                app.viewModel.scenarios.drawingFormModel = new polygonFormModel();
                ko.applyBindings(app.viewModel.scenarios.drawingFormModel, document.getElementById(app.viewModel.currentTocId()+'-drawing-form').children[0]);
                window.dispatchEvent(new Event('resize'));
            },
            error: function (result) {
                console.log('error in scenarios.js: createPolygonDesign');
            }
        });
    };

    self.createCollectionScenario = function() {
      return $.ajax({
        url: '/features/collection/form/',
        success: function(data) {
          app.viewModel.scenarios.collectionForm(true);
          $('#'+app.viewModel.currentTocId()+'-scenario-collection-form > .scenario-collection-form').html(data);
          app.viewModel.scenarios.collectionFormModel = new collectionFormModel();
          ko.applyBindings(app.viewModel.scenarios.collectionFormModel, document.getElementById(app.viewModel.currentTocId()+'-scenario-collection-form').children[0]);
          window.dispatchEvent(new Event('resize'));
        },
        error: function (result) {
          console.log('error in scenarios.js: createCollectionScenario');
        }
      });
    };

    self.createLineDesign = function() {};

    self.createPointDesign = function() {};

    //
    self.addScenarioToMap = function(scenario, options) {
        var scenarioId,
            opacity = .8,
            stroke = 1,
            fillColor = "#00A29B",
            strokeColor = "#00827B",
            zIndex = 1,
            zoomTo = (options && options.zoomTo) || false;

        if ( scenario ) {
            scenarioId = scenario.uid;
            scenario.active(true);
            scenario.visible(true);
        } else {
            scenarioId = options.uid;
        }

        app.state.scenarioId = scenarioId.slice(scenarioId.lastIndexOf('_') + 1);

        var isDrawingModel = false,
            isScenarioModel = false;
        if (scenarioId.indexOf('drawing') !== -1) {
            isDrawingModel = true;
        } else {
            isScenarioModel = true;
        }

        // app.loadingAnimation.show();
        //perhaps much of this is not necessary once a scenario has been added to app.map.layers initially...?
        //(add check for scenario.layer, reset the style and move on?)
        $.ajax( {
            url: '/features/generic-links/links/geojson/' + scenarioId + '/',
            type: 'GET',
            dataType: 'json',
            success: function(retFeatures) {
                if ( scenario ) {
                    var opacity = scenario.opacity();
                    var stroke = scenario.opacity();
                    if (retFeatures.features.length > 0 && retFeatures.features[0].properties.hasOwnProperty('collection')) {
                      display_name = "[" + retFeatures.features[0].properties.collection.name +"] " + scenario.name;
                    } else {
                      display_name = scenario.name;
                    }
                    scenario.display_name = display_name;
                }
                if ( isDrawingModel ) {

                    for (var featIndex = 0; featIndex < retFeatures.features.length; featIndex++){
                        featureId = retFeatures.features[featIndex].properties.uid;
                        $.ajax( {
                            url: '/drawing/get_geometry_orig/' + featureId + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function(data) {
                                var format = new OpenLayers.Format.WKT(),
                                    wkt = data.geometry_orig,
                                    feature = format.read(wkt);
                                scenario.geometry_orig = feature;
                            },
                            error: function(result) {
                                console.log('error in scenarios.js: addScenarioToMap (get_geometry_orig featureId)');
                            }
                        });
                    }

                    if (scenario && scenario.id.indexOf('collection') < 0){
                      style = new OpenLayers.Style(
                        {
                            fillOpacity: scenario.opacity(),
                            strokeOpacity: scenario.opacity(),
                            fillColor: "#C9BE62",
                            strokeColor: "#A99E42",
                            zIndex: zIndex,
                        }
                      );
                    } else {
                      var style = new OpenLayers.Style(
                        {
                          fillOpacity: opacity,
                          strokeOpacity: stroke,
                          zIndex: zIndex,
                        },
                        {
                          rules:[
                            new OpenLayers.Rule({
                              filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "reg_action",
                                value: "close"
                              }),
                              symbolizer:{
                                fillColor: "#FF5555",
                                strokeColor: "#DF3535"
                              }
                            }),
                            new OpenLayers.Rule({
                              filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "reg_action",
                                value: "Close"
                              }),
                              symbolizer:{
                                fillColor: "#FF5555",
                                strokeColor: "#DF3535"
                              }
                            }),
                            new OpenLayers.Rule({
                              filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "reg_action",
                                value: "reopen"
                              }),
                              symbolizer:{
                                fillColor: "#55FF55",
                                strokeColor: "#35DF35"
                              }
                            }),
                            new OpenLayers.Rule({
                              filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "reg_action",
                                value: "Reopen"
                              }),
                              symbolizer:{
                                fillColor: "#55FF55",
                                strokeColor: "#35DF35"
                              }
                            }),
                            new OpenLayers.Rule({
                                // apply this rule if no others apply
                                elseFilter: true,
                                symbolizer: {
                                  fillColor: "#C9BE62",
                                  strokeColor: "#A99E42"
                                }
                            })
                          ]
                        }
                      );
                    }

                }
                var layer = mapSettings.getInitFilterResultsLayer(scenarioId, false);
                // var layer = new OpenLayers.Layer.Vector(
                //     scenarioId,
                //     {
                //         projection: new OpenLayers.Projection('EPSG:3857'),
                //         displayInLayerSwitcher: false,
                //         styleMap: new OpenLayers.StyleMap(style),
                //         scenarioModel: scenario
                //     }
                // );

                layer.addGeoJSONFeatures(retFeatures);
                // layer.addFeatures(new OpenLayers.Format.GeoJSON().read(retFeatures));

                if ( scenario ) {
                    //reasigning opacity here, as opacity wasn't 'catching' on state load for scenarios
                    scenario.opacity(opacity);
                    scenario.layer = layer;
                } else { //create new scenario
                    //only do the following if creating a scenario
                    if (retFeatures.features.length > 0){

                      var properties = retFeatures.features[0].properties;
                      if (properties.hasOwnProperty('collection')){
                        display_name = "[" + properties.collection.name + "] " + properties.name;
                      } else {
                        display_name = properties.name;
                      }
                      if (isDrawingModel) {
                          scenario = new drawingModel({
                              id: properties.uid,
                              uid: properties.uid,
                              name: properties.name,
                              display_name: display_name?display_name:properties.name,
                              description: properties.description,
                              features: layer.features
                          });
                          self.toggleDrawingsOpen('open');
                          self.zoomToScenario(scenario);
                      } else if (isScenarioModel) {
                          scenario = new scenarioModel({
                              id: properties.uid,
                              uid: properties.uid,
                              name: properties.name,
                              display_name: properties.display_name?properties.display_name:properties.name,
                              description: properties.description,
                              features: layer.features
                          });
                          self.toggleScenariosOpen('open');
                          self.zoomToScenario(scenario);
                      } else if (isCollectionModel) {
                        scenario = new collectionModel({
                          id: properties.uid,
                          uid: properties.uid,
                          name: properties.name,
                          display_name: properties.display_name?properties.display_name:properties.name,
                          description: properties.description,
                          features: layer.features
                        });
                        self.toggleCollectionsOpen('open');
                        self.zoomToScenario(scenario);
                      }
                      scenario.layer = layer;
                      scenario.layer.scenarioModel = scenario;
                      scenario.active(true);
                      scenario.visible(true);
                    }

                    $.ajax( {
                        url: '/drawing/get_attributes/' + scenarioId + '/',
                        type: 'GET',
                        dataType: 'json',
                        success: function(result) {
                            if (scenario) {
                              //TODO: figure out when and why this wouldn't have a scenario (on creating empty collection)
                              //    and adjust if necessary
                              scenario.scenarioAttributes(result.attributes);
                            }
                        },
                        error: function (result) {
                            // app.loadingAnimation.hide();
                            console.log('error in scenarios.js: addScenarioToMap (get_attributes scenarioId)');
                        }

                    });

                    //in case of edit, removes previously stored scenario
                    //self.scenarioList.remove(function(item) { return item.uid === scenario.uid } );

                    if (scenario) {

                        if ( isDrawingModel ) {
                            var previousDrawing = ko.utils.arrayFirst(self.drawingList(), function(oldDrawing) {
                                return oldDrawing.uid === scenario.uid;
                            });
                            if ( previousDrawing ) {
                                self.drawingList.replace( previousDrawing, scenario );
                            } else {
                                self.drawingList.push(scenario);
                            }
                            self.drawingList.sort(self.alphabetizeByName);
                        } else {
                            var previousScenario = ko.utils.arrayFirst(self.scenarioList(), function(oldScenario) {
                                return oldScenario.uid === scenario.uid;
                            });
                            if ( previousScenario ) {
                                self.scenarioList.replace( previousScenario, scenario );
                            } else {
                                self.scenarioList.push(scenario);
                            }
                            self.scenarioList.sort(self.alphabetizeByName);
                        }

                    }

                    //self.scenarioForm(false);
                    self.reset();
                }

                if (scenario) {

                    app.map.layers = app.map.getLayers();
                    //app.addVectorAttribution(layer);
                    //in case of edit, removes previously displayed scenario
                    for (var i=0; i<app.map.layers.length; i++) {
                        if (app.map.layers[i].name === scenario.uid) {
                            app.map.removeLayer(app.map.layers[i]);
                            i--;
                        }
                    }
                    if (app.map.hasOwnProperty('scenarioLayer')){
                      app.map.scenarioLayer.removeAllFeatures();
                      app.map.removeLayer(app.map.scenarioLayer);
                    }
                    app.map.scenarioLayer = scenario.layer;
                    app.map.addLayer(app.map.scenarioLayer);
                    //add scenario to Active tab
                    app.viewModel.activeLayers.remove(function(item) { return item.uid === scenario.uid; } );
                    // app.viewModel.activeLayers.unshift(scenario);

                    if (zoomTo) {
                        self.zoomToScenario(scenario);
                    }
                }
                setTimeout(function(){
                  // app.loadingAnimation.hide();
                }, 1500)
            },
            error: function(result) {
                // app.loadingAnimation.hide();
                console.log('error in scenarios.js: addScenarioToMap (geojson scenarioId)');
                app.viewModel.scenarios.errorMessage(result.responseText.split('\n\n')[0]);
            }
        });

    }; // end addScenarioToMap

    self.alphabetizeByName = function(a, b) {
        var name1 = a.display_name.toLowerCase()?a.display_name:a.name.toLowerCase(),
            name2 = b.display_name.toLowerCase()?b.display_name:b.name.toLowerCase();
        if (name1 < name2) {
            return -1;
        } else if (name1 > name2) {
            return 1;
        }
        return 0;
    };

    // activate any lingering designs not shown during loadCompressedState
    self.showUnloadedDesigns = function() {
        var designs = app.viewModel.unloadedDesigns;

        if (designs && designs.length) {
            //the following delay might help solve what appears to be a race condition
            //that prevents the design in the layer list from displaying the checked box icon after loadin
            setTimeout( function() {
                for (var x=0; x < designs.length; x=x+1) {
                    var id = designs[x].id,
                        opacity = designs[x].opacity,
                        isVisible = designs[x].isVisible;

                    if (app.viewModel.layerIndex[id]) {
                        app.viewModel.layerIndex[id].opacity(opacity);
                        app.viewModel.layerIndex[id].activateLayer();
                        for (var i=0; i < app.viewModel.unloadedDesigns.length; i=i+1) {
                            if(app.viewModel.unloadedDesigns[i].id === id) {
                                app.viewModel.unloadedDesigns.splice(i,1);
                                i = i-1;
                            }
                        }
                    }
                }
            }, 400);
        }
    };

    self.loadScenariosFromServer = function() {
        $.ajax({
            url: '/scenario/get_scenarios',
            type: 'GET',
            dataType: 'json',
            success: function (scenarios) {
                self.loadScenarios(scenarios);
                self.scenariosLoaded = true;
                self.showUnloadedDesigns();
                app.viewModel.scenarios.updateDesignsScrollBar();
            },
            error: function (result) {
            }
        });
    };

    //populates scenarioList
    self.loadScenarios = function (scenarios) {
        self.scenarioList.removeAll();
        $.each(scenarios, function (i, scenario) {
            var scenarioViewModel = new scenarioModel({
                id: scenario.uid,
                uid: scenario.uid,
                name: scenario.name,
                display_name: scenario.display_name?scenario.display_name:scenario.name,
                description: scenario.description,
                attributes: scenario.attributes,
                shared: scenario.shared,
                sharedByUsername: scenario.shared_by_username,
                sharedByName: scenario.shared_by_name,
                sharingGroups: scenario.sharing_groups
            });
            self.scenarioList.push(scenarioViewModel);
            app.viewModel.layerIndex[scenario.uid] = scenarioViewModel;
            // self.getAttributes(scenario.uid);
        });
        self.scenarioList.sort(self.alphabetizeByName);
    };

    self.loadDrawingsFromServer = function() {
        $.ajax({
            url: '/drawing/get_drawings',
            type: 'GET',
            dataType: 'json',
            success: function (drawings) {
                self.loadDrawings(drawings);
                self.drawingsLoaded = true;
                self.showUnloadedDesigns();
                app.viewModel.scenarios.updateDesignsScrollBar();
            },
            error: function (result) {
                console.log('error in scenarios.js: loadDrawingsFromServer');
            }
        });
    };
    //populates drawingList
    self.loadDrawings = function (drawings) {
        self.drawingList.removeAll();
        self.drawingListCollections.removeAll();
        self.drawingCollections = [];
        $.each(drawings, function (i, drawing) {
            var drawingCollection = self.drawingInCollection(drawing);
            var drawingViewModel = new drawingModel({
                id: drawing.uid,
                uid: drawing.uid,
                name: drawing.name,
                display_name: drawing.display_name?drawing.display_name:drawing.name,
                collection: drawingCollection,
                description: drawing.description,
                attributes: drawing.attributes,
                shared: drawing.shared,
                sharedByUsername: drawing.shared_by_username,
                sharedByName: drawing.shared_by_name,
                sharingGroups: drawing.sharing_groups,
            });
            self.findDrawingCollections(i, drawingViewModel, drawingCollection);
            app.viewModel.layerIndex[drawing.uid] = drawingViewModel;
            // self.getAttributes(drawing.uid);
        });
        self.loadDrawingsCollections();
        self.drawingList.sort(self.alphabetizeByName);
    };

    self.drawingInCollection = function(drawing) {
        var displayName = drawing.display_name;
        if (displayName.indexOf('[') > -1) {
            var firstIndex = displayName.indexOf('[') + 1;
            return displayName.substring( firstIndex, displayName.indexOf(']') );
        } else {
            return false;
        }
    }

    // accordian for collections in drawings menu
    self.findDrawingCollections = function(i, drawing, collect) {
        // If drawing is not associated with a collection, add it to general list
        if (!collect) {
            self.drawingList.push(drawing);
        } else {
            var newCollection = true;
            if (i === 0) {
                self.pushNewCollection(collect);
            }
            self.drawingCollections.forEach(function(e) {
                if (e.collection.name === collect) {
                    newCollection = false;
                    e.collection.drawings.push(drawing);
                }
            });
            if (newCollection) {
                self.pushNewCollection(collect);
                self.drawingCollections.forEach(function(e) {
                    if (e.collection.name === collect) {
                        e.collection.drawings.push(drawing);
                    }
                });
            }
        }

    }

    self.pushNewCollection = function(collection) {
        self.drawingCollections.push({
            collection: {
                name: collection,
                isActive: ko.observable(false), // set to toggle
                drawings: []
            }
        });
    }

    self.collectionToggleActive = function(data, event) {
        data.collection.isActive(!data.collection.isActive()); //toggle the isActive value between true/false
        self.updateDesignsScrollBar();
    }

    self.loadDrawingsCollections = function() {
        self.drawingCollections.forEach(function(e) {
            self.drawingListCollections.push(e);
        });
    }

    self.loadCollectionsFromServer = function() {
      $.ajax({
        url: '/drawing/get_collections',
        type: 'GET',
        dataType: 'json',
        success: function (collections) {
          self.loadCollections(collections);
          self.collectionsLoaded = true;
          self.showUnloadedDesigns();
          app.viewModel.scenarios.updateDesignsScrollBar();
        },
        error: function (result) {
          console.log('error in scenarios.js: loadCollectionsFromServer');
        }
      });
    };

    self.loadCollections = function(collections) {
      self.collectionList.removeAll();
      $.each(collections, function (i, collection) {
        var collectionViewModel = new collectionModel({
          id: collection.uid,
          uid: collection.uid,
          name: collection.name,
          display_name: collection.display_name?collection.display_name:collection.name,
          description: collection.description,
          attributes:  collection.attributes,
          shared: collection.shared,
          sharedByUsername: collection.shared_by_username,
          sharedByName: collection.shared_by_name,
          sharingGroups: collection.sharing_groups
        });
        self.collectionList.push(collectionViewModel);
        app.viewModel.layerIndex[collection.uid] = collectionViewModel;
        // self.getAttributes(collection.uid);
      });
      self.collectionList.sort(self.alphabetizeByName);
      app.viewModel.scenarios.loadDrawingsFromServer();
      app.viewModel.scenarios.updateDesignsScrollBar();
    };

    self.aggregateTranslate = function(inObjList) {
      var outObjList = [];
      for (var i=0; i < inObjList.length; i++) {
        var inObj = inObjList[i];
        var outObj = {};
        outObj['data'] = inObj['data'];
        outObj['display'] = inObj['title'];
        outObjList.push(outObj);
      }
      return outObjList;
    };

    self.getAttributes = function(uid) {
      uid = uid;
      $.ajax({
        url: '/drawing/get_attributes/' + uid,
        type: 'GET',
        dataType: 'json',
        success: function(data){
          if (app.viewModel.layerIndex[uid].hasOwnProperty('attributes')){
            app.viewModel.layerIndex[uid].attributes(data);
          }
          app.viewModel.layerIndex[uid].scenarioAttributes(data.attributes);
          var activeLayer = app.viewModel.activeLayers().find(function(obj){return obj.uid == uid;})
          if (activeLayer) {
            activeLayer.attributes(data);
          }
          if (data.attributes.filter(function(obj){return obj.hasOwnProperty('Status');}).length > 0){
            console.log('data not yet loaded. Retrying...');
            setTimeout(app.viewModel.scenarios.getAttributes(uid), 5000);
          } else {
            if (app.viewModel.layerIndex[uid].showingLayerAttribution()){
              var aggAttrs = {};
              aggAttrs[app.viewModel.layerIndex[uid].name] = self.aggregateTranslate(data.attributes);
              app.viewModel.aggregatedAttributes(aggAttrs);
            }
          }
        },
        error: function(response){
          console.log('error in scenarios.js: getAttributes');
          window.alert(response.responseText);
        }
      });
    };

    self.loadLeaseblockLayer = mapSettings.loadFilterLayer;
    self.leaseblockList = [];

    //populates leaseblockList
    self.loadLeaseblocks = function (ocsblocks) {
        self.leaseblockList = ocsblocks;
    };

    self.cancelShare = function() {
        self.sharingLayer().temporarilySelectedGroups.removeAll();
    };

    //SHARING DESIGNS
    self.submitShare = function() {
        self.sharingLayer().selectedGroups(self.sharingLayer().temporarilySelectedGroups().slice(0));
        var data = { 'scenario': self.sharingLayer().uid, 'groups': self.sharingLayer().selectedGroups() };
        $.ajax( {
            url: '/scenario/share_design',
            data: data,
            type: 'POST',
            dataType: 'json',
            error: function(result) {
                console.log('error in scenarios.js: submitShare');
            }
        });
    };

    self.cancelAssociate = function() {
      self.associatedDrawing().temporarilySelectedScenarios.removeAll();
    };

    self.submitAssociate = function() {
      self.associatedDrawing().selectedScenarios(self.associatedDrawing().temporarilySelectedScenarios().slice(0));
      var data = {
        'scenario': self.associatedDrawing().uid,
        'collections': self.associatedDrawing().selectedScenarios()
      };
      $.ajax( {
        url: '/scenario/associate_scenario',
        data: data,
        type: 'POST',
        dataType: 'json',
        success: function(data) {
            for (var data_index = 0; data_index < data.length; data_index++) {
                app.viewModel.scenarios.addScenarioToMap(null, {uid: data[data_index].uid});
            }
            self.associatedDrawing().temporarilySelectedScenarios.removeAll();
            app.viewModel.scenarios.loadCollectionsFromServer();
        },
        error: function(result) {
          console.log('error in scenarios.js: submitAssociate');
          window.alert(result.responseText);
          self.associatedDrawing().temporarilySelectedScenarios.removeAll();
        }
      });
      self.associatedDrawing().temporarilySelectedScenarios.removeAll();
    };

    self.cancelCompare = function() {
      self.comparisonCollection().temporarilySelectedScenarios.removeAll();
    };

    self.submitCompare = function() {
      console.log('submit compare!');
      self.comparisonCollection().selectedScenarios(self.comparisonCollection().temporarilySelectedScenarios().slice(0));
      var data = {
        'scenario': self.comparisonCollection().uid,
        'collections': self.comparisonCollection().selectedScenarios()
      };
      // app.loadingAnimation.show();
      $.ajax( {
        url: '/scenario/compare_scenario',
        data: data,
        type: 'POST',
        dataType: 'json',
        success: function(data) {
          // app.loadingAnimation.hide();
          attr_list = data[0];
          report_data = data[1];
          download_link = data[2];
          app.viewModel.scenarios.showComparisonReportModal(attr_list,report_data,download_link);
        },
        error: function(result) {
          // app.loadingAnimation.hide();
          console.log('error in scenarios.js: submitCompare');
          window.alert(result.responseText);
        }
      });
    };

    self.setBaseLine = function(col_id, data) {
      // Update observable value array with relative comparison values
      app.viewModel.scenarios.setComparisonReportBaseline(col_id);
      $('td.collection-report-cell').removeClass('active');
      if (col_id !== 0) {
        column = col_id + 1;
        $('td:nth-of-type('+ column + ').collection-report-cell').addClass('active');
      }
    };

    self.loadDesigns = function() {

        if ( !self.drawingsLoaded ) {
            // load the scenarios
            // self.loadScenariosFromServer();

            // load the drawing
            self.loadDrawingsFromServer();

            // load the collections
            self.loadCollectionsFromServer();

            $.ajax({
                url: '/scenario/get_sharing_groups',
                type: 'GET',
                dataType: 'json',
                success: function (groups) {
                    app.viewModel.scenarios.sharingGroups(groups);
                    if (groups.length) {
                        app.viewModel.scenarios.hasSharingGroups(true);
                    }
                },
                error: function (result) {
                    console.log('error in scenarios.js: loadDesigns');
                }
            });
        }
    }

    return self;
} // end scenariosModel


app.viewModel.scenarios = new scenariosModel();

$('.designsTab').on('show', function (e) {
    app.viewModel.scenarios.loadDesigns();
});
