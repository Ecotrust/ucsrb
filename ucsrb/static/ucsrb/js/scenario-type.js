var scenarioType = {
  currentScenarioType: 0,
  scenarioTypes: [
    'select',
    'filter',
    'draw'
  ],
  get function() {
    return this.currentScenarioType
  },
  set current(scenarioType) {
    this.currentScenarioType = scenarioType;
  }
}
