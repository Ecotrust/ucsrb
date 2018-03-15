app.state = {
    method: '',
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
    stepVal: null,
    set setMethod(method) {
        this.method = method;
        this.focusArea.method = method;
    },
    set navHeight(height) {
        this.nav = height;
    },
    set instructions(instruction) {
        $('#instruction').html(instruction);
    },
    set step(step) {
        this.stepVal = step;
        if (step === null || step === 'reset') {
            app.state.panelContent = '';
            app.panel.getPanelContentElement.innerHTML = '<div id="scenarios"></div><div id="scenario_form"></div><div id="results"></div>';
            app.panel.moveRight();
        } else {
            app.state.instructions = app.nav.instructions[app.state.methodState][step];
            if (app.nav.stepActions[app.state.methodState][step]) {
              app.nav.stepActions[app.state.methodState][step]();
            }
        }
        //TODO: Recognize and trigger filtering/drawing steps.
    },
    set setFocusArea(focusAreaObject) {
      this.focusArea.method = this.method;
      this.focusArea.id = focusAreaObject.id;
      this.focusArea.geometry = focusAreaObject.geojson;
    },
    get methodState() {
        return this.method;
    },
    get panelContent() {
        return this.panel.content;
    },
    get focusAreaState() {
        return this.focusArea;
    },
    get saveState() {
        return {
            method: this.method,
            focusArea: this.focusAreaState,
            nav: this.nav,
            step: this.step,
        }
    }
}
