app.prescription = {
  updateTreatmentSectionCount: function() {
    var count = app.map.selection.select.getFeatures().getArray().length;
    $('#selected-treatments-count').html(count);
    if (count < 1) {
      $('.prescription-selection-row button').prop('disabled', true);
      $('#clear-all-treatments-button').prop('disabled', true);
      // $('#rx-submit-button').prop('disabled', false);
    } else {
      $('.prescription-selection-row button').prop('disabled', false);
      $('#clear-all-treatments-button').prop('disabled', false);
      // $('#rx-submit-button').prop('disabled', true);
    }
  },
  selectAction: function(feature) {
    // Update selection count
    app.prescription.updateTreatmentSectionCount();
    // prevent un-selection of other
  },
  selectAllTreatments: function() {
    var all_features = app.map.treatmentLayer.getSource().getFeatures();
    for (var i = 0; i < all_features.length; i++) {
      var feature = all_features[i];
      if (app.map.selection.select.getFeatures().getArray().indexOf(feature) < 0) {
        app.map.selection.select.getFeatures().push(feature);
      }
    }

    // Update selection count
    app.prescription.updateTreatmentSectionCount();
  },
  deselectAllTreatments: function() {
    app.map.selection.select.getFeatures().clear();
    app.prescription.updateTreatmentSectionCount();
  },
  applyRx: function(prescription) {
    var selected_features = app.map.selection.select.getFeatures().getArray();
    for (var i=0; i < selected_features.length; i++) {
      var feature = selected_features[i];
      feature.set('prescription', prescription);
    }
    app.prescription.deselectAllTreatments();
  },
  applyNotr: function() { app.prescription.applyRx('notr');},
  applyMb16: function() { app.prescription.applyRx('mb16');},
  applyMb25: function() { app.prescription.applyRx('mb25');},
  applyBurn: function() { app.prescription.applyRx('burn');},
  applyIdeal: function() { app.prescription.applyRx('flow');},
  submitTreatments: function() {
    var selectedFeatures = app.map.selection.select.getFeatures().getArray();
    if (selectedFeatures.length > 0) {
      alert("You have selected features that you have not updated. Please finish applying prescriptions or clear your selection before proceeding.");
    } else {
      var allFeatures = app.map.treatmentLayer.getSource().getFeatures();
      // build json of feature IDs and prescriptions
      var treatment_json = [];
      for (var i = 0; i < allFeatures.length; i++) {
        var feat = allFeatures[i];
        treatment_json.push({id: feat.get('id'), prescription: feat.get('prescription')});
      }
      app.request.submitPrescriptions(treatment_json);
    }
  }
};
