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
        geometry: {},
        pp_id: 0
    },
    nav: 'tall',
    stepVal: 0,
    set setMethod(method) {
        this.method = method;
        this.focusArea.method = method;
    },
    set panelContent(content) {
        this.panel.content = content;
    },
    set panelheight(height) {
        this.panel.height = height;
    },
    set navHeight(height) {
        this.nav = height;
    },
    set instructions(instruction) {
        $('#instruction').html(instruction);
    },
    set step(step) {
        app.state.instructions = app.nav.instructions[app.state.methodState][step];
        this.stepVal = step;
        //TODO: Recognize and trigger filtering/drawing steps.
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
            focusArea: this.focusAreaState
        }
    }
}
