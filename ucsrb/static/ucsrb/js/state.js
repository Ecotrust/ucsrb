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
    },
    set navHeight(height) {
        this.nav = height;
    },
    set instructions(instruction) {
        $('#instruction').html(instruction);
    },
    set step(step) {
      this.stepVal = step;
      app.state.instructions = app.nav.instructions[app.state.getMethod][step];
      if (app.nav.stepActions[step]) {
        app.nav.stepActions[step]();
      } else if (app.nav.stepActions[app.state.getMethod][step]) {
        app.nav.stepActions[app.state.getMethod][step]();
      }
        //TODO: Recognize and trigger filtering/drawing steps.
    },
    set setFocusArea(focusAreaObject) {
      this.focusArea.method = this.method;
      this.focusArea.id = focusAreaObject.id;
      this.focusArea.geometry = focusAreaObject.geojson;
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
    get saveState() {
        return {
            method: this.method,
            focusArea: this.focusAreaState,
            nav: this.nav,
            step: this.step,
        }
    }
}
