app.state = {
  scenarioType: '',
  scenarioPanel: {
    content: '',
    position: '',
    panelHeight: '',
    step: 0
  },
  get type() {
    return this.scenarioType;
  },
  get panel() {
    return this.scenarioPanel;
  },
}
