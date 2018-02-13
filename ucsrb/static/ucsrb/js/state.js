app.state = {
    method: '',
    panel: {
        content: '',
        position: '',
    },
    instructions: '',
    focusArea: {
        method: '',
        geometry: {},
        pp_id: 0,
    },
    nav: 'tall',
    step: 0,
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
        app.state.instructions = app.nav.instructions[app.state.methodState][step];
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
        }
    }
}
