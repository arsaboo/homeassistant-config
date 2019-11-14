class GapCard extends HTMLElement {

  setConfig(config) {
    this.height = ('height' in config) ? config.height : 50;
    this.size = ('size' in config) ? config.size :  Math.ceil(this.height/50);
    this.style.setProperty('height', this.height + 'px');
  }

  getCardSize() {
    return this.size;
  }
}

customElements.define('gap-card', GapCard);
