var scenarioType = {
  currentScenarioType: 0,
  scenarioTypes: [
    'select',
    'filter',
    'draw'
  ],
  get current() {
    return this.currentScenarioType;
  },
  set current(scenarioType) {
    this.currentScenarioType = scenarioType;
  }
}
