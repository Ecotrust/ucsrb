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
    // TODO add type check and flow position check
    this.currentScenarioType = scenarioType;
  }
};

var scenarioTypePanel = {
  currentStep: 0,
  panelPosition: '',
  panelHeight: 0,
  panelContent: '',
  get step() {
    return this.currentStep;
  },
  get position() {
    return this.panelPosition;
  },
  get height() {
    return this.panelHeight;
  },
  get content() {
    return this.panelContent;
  },
  set step(step) {
    this.currentStep = step;
  },
  set position(position) {
    this.panelPosition = position;
  },
  set height(height) {
    this.panelHeight = height;
  },
  set content(content) {
    this.panelContent = content;
  },
  showNextBtn: function() {
    $('#next-step').addClass('show');
  },
  showPrevBtn: function() {
    $('#prev-step').addClass('show');
  },
  hideNextBtn: function() {
    $('#next-step').removeClass('show');
  },
  hidePrevBtn: function() {
    $('#prev-step').removeClass('show');
  },
  setHeight: function() {
    $('#right-panel').css('height', scenarioTypePanel.height);
  },
  setPosition: function() {
    if (scenarioTypePanel.position == 'left') {
      $('#right-panel').css('right', 'auto');
      $('#right-panel').css('left', '0');
    } else if (scenarioTypePanel.position == 'right') {
      $('#right-panel').css('left', 'auto');
      $('#right-panel').css('right', '0');
    }
  },
  setContent: function() {
    $('.content').html(scenarioTypePanel.content);
  },
  setPanel: function(position, height, content) {
    scenarioTypePanel.position  = position;
    scenarioTypePanel.height    = height;
    scenarioTypePanel.content   = content;
  },
  updatePanel: function() {
    scenarioTypePanel.showNextBtn();
    if (scenarioTypePanel.step > 1) {
      scenarioTypePanel.showPrevBtn();
    } else {
      scenarioTypePanel.hidePrevBtn();
    }
    scenarioTypePanel.setHeight();
    scenarioTypePanel.setPosition();
    scenarioTypePanel.setContent();
  }
};
