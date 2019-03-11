customElements.whenDefined('card-tools').then(() => {
let cardTools = customElements.get('card-tools');
class LayoutCard extends cardTools.LitElement {

  async setConfig(config) {
    this.config = config;
    this.layout = config.layout || 'auto';
    this.minCols = config.column_num || 1;
    this.maxCols = config.max_columns || 100;
    this.colWidth = config.column_width || 300;
    this.maxWidth = config.max_width || 500;
    this.minHeight = config.min_height || 5;
    this.rtl = config.rtl || false;
    this.cardSize = 1;

    window.addEventListener('resize', () => this.build());
    window.addEventListener('hass-open-menu', () => setTimeout(() => this.build(), 100));
    window.addEventListener('hass-close-menu', () => setTimeout(() => this.build(), 100));
  }

  render() {
    return cardTools.LitHtml`
    <div id="columns"></div>
    `;
  }

  firstUpdated() {
    if(this.parentElement && this.parentElement.id !== "view")
    {
      this.style.padding = "0";
    }
    if(this.rtl)
      this.shadowRoot.querySelector("#columns").style.flexDirection = 'row-reverse';
    this.build();
    this._cardModder = {
      target: this,
      styles: this.shadowRoot.querySelector("style")
    };
  }

  static get styles() {
    return cardTools.LitCSS`
      :host {
        padding: 8px 4px 0;
        display: block;
      }

      #columns {
        display: flex;
        flex-direction: row;
        justify-content: center;
      }

      .column {
        flex-basis: 0;
        flex-grow: 1;
        overflow-x: hidden;
      }

      .column > * {
        display: block;
        margin: 4px 4px 8px;
      }

      .column > *:first-child {
        margin-top: 0;
      }
    `;
  }

  make_cards() {
    this.cards = this.config.cards.map((c) => {
      if (typeof c === 'string') return c;
      const card = cardTools.createCard(c);
      if(this._hass) card.hass = this._hass;
      this.appendChild(card); // Place card in DOM to get size
      return card;
    });
  }

  update_columns() {
    const width = (this.shadowRoot && this.shadowRoot.querySelector("#columns").clientWidth) || (this.parentElement && this.parentElement.clientWidth);
    this.colNum = Math.floor(width / this.colWidth);
    this.colNum = Math.max(this.colNum, this.minCols);
    this.colNum = Math.min(this.colNum, this.maxCols);
  }

  build() {
    const root = this.shadowRoot.querySelector("#columns");
    while(root.lastChild) {
      root.removeChild(root.lastChild);
    }

    this.update_columns();

    if(!this.cards) this.make_cards();

    let cols = [];
    let colSize = [];
    for(let i = 0; i < this.colNum; i++) {
      cols.push([]);
      colSize.push(0);
    }

    const shortestCol = () => {
      let i = 0;
      for(let j = 0; j < this.colNum; j++) {
        if(colSize[j] < this.min_height)
          return j;
        if(colSize[j] < colSize[i])
          i = j;
      }
      return i;
    }

    let i = 0;
    this.cards.forEach((c) => {
      const isBreak = (typeof(c) === 'string');
      const sz = c.getCardSize ? c.getCardSize() : 1;

      switch(this.layout) {
        case 'horizontal':
          if(i >= this.colNum) i = 0;
          i += 1;
          if(isBreak) break;
          cols[i-1].push(c);
          colSize[i-1] += sz;
          break;
        case 'vertical':
          if(isBreak){
            i += 1;
            if(i >= this.colNum)
              i = 0;
            break;
          }
          cols[i].push(c);
          colSize[i] += sz;
          break;
        case 'auto':
        default:
          if(isBreak) break;
          cols[shortestCol()].push(c);
          colSize[shortestCol()] += sz;
          break;
      }
    });

    cols = cols.filter((c) => c.length > 0);
    cols.forEach((c, i) => {
      const div = document.createElement('div');
      div.classList.add('column');
      c.forEach((e) => div.appendChild(e));
      root.appendChild(div);
      if(cols.length > 1 && typeof(this.maxWidth) === 'object') {
        div.style.setProperty('max-width', this.maxWidth[i]);
      } else {
        div.style.setProperty('max-width', this.maxWidth+'px');
      }
    });

    this.cardSize = Math.max.apply(null, colSize);
  }

  set hass(hass) {
    this._hass = hass;
    if(this.cards)
      this.cards
        .filter((c) => typeof(c) !== 'string')
        .forEach((c) => c.hass = hass);
  }

  getCardSize() {
    return this.cardSize;
  }

}

customElements.define('layout-card', LayoutCard);
});
window.setTimeout(() => {
  if(customElements.get('card-tools')) return;
  customElements.define('layout-card', class extends HTMLElement{
    setConfig() { throw new Error("Can't find card-tools. See https://github.com/thomasloven/lovelace-card-tools");}
  });
}, 2000);
