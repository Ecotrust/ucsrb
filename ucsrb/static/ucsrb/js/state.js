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
        this.step = val;

        // update navigation based on step
        // reset, initial, ...
        if (app.nav.stepActions[val]) {
            app.nav.stepActions[val]();
        // select, filter, ...
        } else if (app.nav.stepActions[app.state.getMethod][val]) {
            app.nav.stepActions[app.state.getMethod][val]();
        }

        // update instructions content based on step
        // reset, initial, ...
        if (app.nav.instructions[val]) {
            app.state.instructions = app.nav.instructions[val];
        // select, filter, ...
        } else if (app.nav.instructions[app.state.getMethod][val]) {
            app.state.instructions = app.nav.instructions[app.state.getMethod][val];
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
