app.state = {
  method: '',
  panel: {
    content: '',
    position: '',
    height: '',
  },
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
  set panelContent(content) {
    this.panel.content = content;
    app.panel.setRPanelContent(content);
  },
  set panelheight(height) {
    this.panel.height = height;
  },
  set navHeight(height) {
    this.nav = height;
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
