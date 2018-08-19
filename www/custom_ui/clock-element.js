// based on https://codepen.io/mohebifar/pen/KwdeMz
class ClockElement extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  set hass(hass) {
  }

  setConfig(config) {
    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);
    root.appendChild(this._buildWire());
    this._updateCLock(root.querySelector('svg'));
  }

  getCardSize() {
    return 1;
  }

  _buildWire() {
    const elemContainer = document.createElement('div');
    elemContainer.appendChild(this._htmlToElement(`
      <svg width="200" height="200">
        <filter id="innerShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur" />
          <feOffset in="blur" dx="2.5" dy="2.5" />
        </filter>
        <g>
          <circle id="shadow" style="fill:rgba(0,0,0,0.1)" cx="97" cy="100" r="87" filter="url(#innerShadow)"></circle>
          <circle id="circle" style="stroke: #FFF; stroke-width: 12px; fill:#20B7AF" cx="100" cy="100" r="80"></circle>
        </g>
        <g>
          <line x1="100" y1="100" x2="100" y2="55" transform="rotate(80 100 100)" style="stroke-width: 3px; stroke: #fffbf9;" id="hourhand">
            <animatetransform attributeName="transform" attributeType="XML" type="rotate" dur="43200s" repeatCount="indefinite" />
          </line>
          <line x1="100" y1="100" x2="100" y2="40" style="stroke-width: 4px; stroke: #fdfdfd;" id="minutehand">
            <animatetransform attributeName="transform" attributeType="XML" type="rotate" dur="3600s" repeatCount="indefinite" />
          </line>
          <line x1="100" y1="100" x2="100" y2="30" style="stroke-width: 2px; stroke: #C1EFED;" id="secondhand">
            <animatetransform attributeName="transform" attributeType="XML" type="rotate" dur="60s" repeatCount="indefinite" />
          </line>
        </g>
        <circle id="center" style="fill:#128A86; stroke: #C1EFED; stroke-width: 2px;" cx="100" cy="100" r="3"></circle>
      </svg>`));

    const style = document.createElement('style');
    style.textContent = this._buildStyle();
    elemContainer.appendChild(style);

    return elemContainer
  }


  _updateCLock(svg) {
    let hands = [];
    hands.push(svg.querySelector('#secondhand > *'));
    hands.push(svg.querySelector('#minutehand > *'));
    hands.push(svg.querySelector('#hourhand > *'));

    const cx = 100;
    const cy = 100;

    const date = new Date();
    const hoursAngle = 360 * date.getHours() / 12 + date.getMinutes() / 2;
    const minuteAngle = 360 * date.getMinutes() / 60;
    const secAngle = 360 * date.getSeconds() / 60;

    hands[0].setAttribute('from', [secAngle, cx, cy].join(' '));
    hands[0].setAttribute('to', [secAngle + 360, cx, cy].join(' '));
    hands[1].setAttribute('from', [minuteAngle, cx, cy].join(' '));
    hands[1].setAttribute('to', [minuteAngle + 360, cx, cy].join(' '));
    hands[2].setAttribute('from', [hoursAngle, cx, cy].join(' '));
    hands[2].setAttribute('to', [hoursAngle + 360, cx, cy].join(' '));

    for (let i = 1; i <= 12; i++) {
      const el = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      el.setAttribute('x1', '100');
      el.setAttribute('y1', '30');
      el.setAttribute('x2', '100');
      el.setAttribute('y2', '40');
      el.setAttribute('transform', 'rotate(' + (i * 360 / 12) + ' 100 100)');
      el.setAttribute('style', 'stroke: #ffffff;');
      svg.appendChild(el);
    }
  }

  _buildStyle() {
    return `
      :host {

      }
      svg {
        display: block;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }

      .filler {
        background: #20B7AF;
        position: absolute;
        bottom: 50%;
        top: 0;
        left: 0;
        right: 0;
      }`;

  }

  _htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
  }


}

window.customElements.define('clock-element', ClockElement);
