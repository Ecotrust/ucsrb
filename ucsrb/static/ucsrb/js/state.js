app.state = {
    method: '',
    scenarioId: null,
    panel: {
        content: '',
        position: '',
        height: ''
    },
    instructions: '',
    focusArea: {
        method: '',
        geometry: null,
        id: null
    },
    nav: 'tall',
    step: 0,
    formModel: null,
    set setMethod(method) {
        this.method = method;
    },
    set navHeight(height) {
        // set state height value
        this.nav = height;

        if (height === 'short') {
            // set nav to befinning height
            app.nav.short();
        } else if (height === 'tall') {
            // set nav to use small icons and reduce height
            app.nav.short();
        }
    },
    set instructions(instruction) {
        $('#instruction').html(instruction);
    },
    set setStep(val) {
        // set state step value
        if (typeof(val) == "number" || typeof(val) == "string" || (val.length == 2 && !val[1])) {
          if (typeof(val) == "number" || typeof(val) == "string") {
            this.step = val;
          } else {
            this.step = val[0];
          }
          // update navigation based on step
          // reset, initial, ...
          if (app.nav.stepActions[val]) {
              app.nav.stepActions[val]();
          // select, filter, ...
          } else if (app.nav.stepActions[app.state.getMethod][val]) {
              app.nav.stepActions[app.state.getMethod][val]();
          }
        } else {
          this.step = val[0];
          var arguments_obj = val[1];
          // update navigation based on step
          // reset, initial, ...
          if (app.nav.stepActions[this.step]) {
            app.nav.stepActions[this.step](arguments_obj);
            // select, filter, ...
          } else if (app.nav.stepActions[app.state.getMethod][this.step]) {
            app.nav.stepActions[app.state.getMethod][this.step](arguments_obj);
          }
        }

        // update instructions content based on step
        // reset, initial, ...
        if (app.nav.instructions[this.step]) {
            app.state.instructions = app.nav.instructions[this.step];
        // select, filter, ...
        } else if (app.nav.instructions[app.state.getMethod][this.step]) {
            app.state.instructions = app.nav.instructions[app.state.getMethod][this.step];
        }

        //TODO: Recognize and trigger filtering/drawing steps.
    },
    set setFocusArea(focusAreaObject) {
        this.focusArea.method = this.method;
        this.focusArea.id = focusAreaObject.id;
        this.focusArea.geometry = focusAreaObject.geojson;
    },
    set showMapControls(show) {
        app.map.toggleMapControls(show);
    },
    get getMethod() {
        return this.method;
    },
    get panelContent() {
        return this.panel.content;
    },
    get focusAreaState() {
        return this.focusArea;
    },
    get getFormModel() {
        return this.formModel;
    },
    get saveState() {
        return {
            method: this.method,
            focusArea: this.focusArea,
            nav: this.nav,
            step: this.step,
        }
    }
}
