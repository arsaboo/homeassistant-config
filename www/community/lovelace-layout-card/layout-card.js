!function(t){var e={};function n(o){if(e[o])return e[o].exports;var i=e[o]={i:o,l:!1,exports:{}};return t[o].call(i.exports,i,i.exports,n),i.l=!0,i.exports}n.m=t,n.c=e,n.d=function(t,e,o){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:o})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var o=Object.create(null);if(n.r(o),Object.defineProperty(o,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var i in t)n.d(o,i,function(e){return t[e]}.bind(null,i));return o},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=1)}([function(t){t.exports=JSON.parse('{"name":"layout-card","version":"1.2.0","description":"","private":true,"scripts":{"build":"webpack","watch":"webpack --watch --mode=development","update-card-tools":"npm uninstall card-tools && npm install thomasloven/lovelace-card-tools"},"author":"Thomas Lovén","license":"MIT","devDependencies":{"webpack":"^4.41.5","webpack-cli":"^3.3.10"},"dependencies":{"card-tools":"github:thomasloven/lovelace-card-tools"}}')},function(t,e,n){"use strict";n.r(e);const o=customElements.get("home-assistant-main")?Object.getPrototypeOf(customElements.get("home-assistant-main")):Object.getPrototypeOf(customElements.get("hui-view")),i=o.prototype.html,s=o.prototype.css;function r(){return document.querySelector("hc-main")?document.querySelector("hc-main").hass:document.querySelector("home-assistant")?document.querySelector("home-assistant").hass:void 0}function a(t,e,n=null){if((t=new Event(t,{bubbles:!0,cancelable:!1,composed:!0})).detail=e||{},n)n.dispatchEvent(t);else{var o=function(){var t=document.querySelector("hc-main");return t=t?(t=(t=(t=t&&t.shadowRoot)&&t.querySelector("hc-lovelace"))&&t.shadowRoot)&&t.querySelector("hui-view"):(t=(t=(t=(t=(t=(t=(t=(t=(t=(t=(t=document.querySelector("home-assistant"))&&t.shadowRoot)&&t.querySelector("home-assistant-main"))&&t.shadowRoot)&&t.querySelector("app-drawer-layout partial-panel-resolver"))&&t.shadowRoot||t)&&t.querySelector("ha-panel-lovelace"))&&t.shadowRoot)&&t.querySelector("hui-root"))&&t.shadowRoot)&&t.querySelector("ha-app-layout #view"))&&t.firstElementChild}();o&&o.dispatchEvent(t)}}let c=window.cardHelpers;const l=new Promise(async(t,e)=>{c&&t(),window.loadCardHelpers&&(c=await window.loadCardHelpers(),window.cardHelpers=c,t())});function d(t,e){const n=document.createElement("hui-error-card");return n.setConfig({type:"error",error:t,origConfig:e}),n}function u(t,e){if(!e||"object"!=typeof e||!e.type)return d(`No ${t} type configured`,e);let n=e.type;if(n=n.startsWith("custom:")?n.substr("custom:".length):`hui-${n}-${t}`,customElements.get(n))return function(t,e){let n=document.createElement(t);try{n.setConfig(JSON.parse(JSON.stringify(e)))}catch(t){n=d(t,e)}return l.then(()=>{a("ll-rebuild",{},n)}),n}(n,e);const o=d(`Custom element doesn't exist: ${n}.`,e);o.style.display="None";const i=setTimeout(()=>{o.style.display=""},2e3);return customElements.whenDefined(n).then(()=>{clearTimeout(i),a("ll-rebuild",{},o)}),o}function h(t,e,n){t.forEach(t=>{if(!t)return;const o=e[function(){let t=0;for(let o=0;o<e.length;o++){if(e[o].length<n.min_height)return o;e[o].length<e[t].length&&(t=o)}return t}()];o.appendChild(t),o.length+=t.getCardSize?t.getCardSize():1})}class m extends o{static get properties(){return{hass:{},_config:{}}}async setConfig(t){this._config={min_height:5,column_width:300,max_width:t.column_width||"500px",min_columns:t.column_num||1,max_columns:100,...t},this.cards=[],this.columns=[],this.resizer=new ResizeObserver(t=>{for(let e of t)if(e.contentRect&&e.contentRect.width)return this._layoutWidth=e.contentRect.width,void this.place_cards()}),this.resizer.observe(this)}connectedCallback(){super.connectedCallback();let t=this.parentElement,e=10;for(;e--&&t&&("HUI-PANEL-VIEW"===t.tagName&&this.classList.add("panel"),"DIV"!==t.tagName););}async firstUpdated(){window.addEventListener("location-changed",()=>{""===location.hash&&setTimeout(()=>this.place_cards(),100)})}async updated(t){if(!this.cards.length&&(this._config.entities&&this._config.entities.length||this._config.cards&&this._config.cards.length)){this.clientWidth;this.cards=await this.build_cards(),this.place_cards()}t.has("hass")&&this.hass&&this.cards&&this.cards.forEach(t=>{t&&(t.hass=this.hass)})}async build_card(t){if("break"===t)return null;const e={...t,...this._config.card_options},n=function(t){return c?c.createCardElement(t):u("card",t)}(e);return n.hass=r(),n.style.gridColumn=e.gridcol,n.style.gridRow=e.gridrow,this.shadowRoot.querySelector("#staging").appendChild(n),new Promise((t,e)=>n.updateComplete?n.updateComplete.then(()=>t(n)):t(n))}async build_cards(){const t=this.shadowRoot.querySelector("#staging");for(;t.lastChild;)t.removeChild(t.lastChild);return Promise.all((this._config.entities||this._config.cards).map(t=>this.build_card(t)))}place_cards(){"grid"!==this._config.layout&&(this.columns=function(t,e,n){const o=t=>"string"==typeof t&&t.endsWith("%")?Math.floor(e*parseInt(t)/100):parseInt(t);let i=0;if("object"==typeof n.column_width){let t=e;for(;t>0;){let e=n.column_width[i];void 0===e&&(e=n.column_width.slice(-1)[0]),t-=o(e),i+=1}i=Math.max(i-1,1)}else i=Math.floor(e/o(n.column_width));i=Math.max(i,n.min_columns),i=Math.min(i,n.max_columns),i=Math.max(i,1);let s=[];for(let t=0;t<i;t++){const t=document.createElement("div");t.classList.add("column"),t.classList.add("cards"),t.length=0,s.push(t)}switch(n.layout){case"horizontal":!function(t,e,n){let o=0;t.forEach(t=>{if(o+=1,!t)return;const n=e[(o-1)%e.length];n.appendChild(t),n.length+=t.getCardSize?t.getCardSize():1})}(t,s);break;case"vertical":!function(t,e,n){let o=0;t.forEach(t=>{if(!t)return void(o+=1);const n=e[o%e.length];n.appendChild(t),n.length+=t.getCardSize?t.getCardSize():1})}(t,s);break;case"auto":default:h(t,s,n)}return s=s.filter(t=>t.childElementCount>0),s}(this.cards,this._layoutWidth||1,this._config),this._config.rtl&&this.columns.reverse(),this.format_columns(),this.requestUpdate())}format_columns(){const t=(t,e,n,o="px")=>{if(void 0===this._config[e])return"";let i=`${t}: `;const s=this._config[e];return"object"==typeof s?s.length>n?i+=`${s[n]}`:i+=`${s.slice(-1)}`:i+=`${s}`,i.endsWith("px")||i.endsWith("%")||(i+=o),i+";"};for(const[e,n]of this.columns.entries()){const o=[t("max-width","max_width",e),t("min-width","min_width",e),t("width","column_width",e),t("flex-grow","flex_grow",e,"")];n.style.cssText="".concat(...o)}}getCardSize(){if(this.columns)return Math.max.apply(Math,this.columns.map(t=>t.length))}render(){return"grid"===this._config.layout?i`
        <div id="staging" class="grid"
        style="
        display: grid;
        grid-template-rows: ${this._config.gridrows};
        grid-template-columns: ${this._config.gridcols};
        "></div>
      `:i`
      <div id="columns"
      style="
      ${this._config.justify_content?`justify-content: ${this._config.justify_content};`:""}
      ">
        ${this.columns.map(t=>i`
          ${t}
        `)}
      </div>
      <div id="staging"></div>
    `}static get styles(){return s`
      :host {
        padding: 0;
        display: block;
        margin-bottom: 0!important;
      }
      :host(.panel) {
        padding: 0 4px;
        margin-top: 8px;
      }

      #columns {
        display: flex;
        flex-direction: row;
        justify-content: center;
        margin-top: -8px;
      }

      .column {
        flex-basis: 0;
        flex-grow: 1;
        overflow-x: hidden;
      }
      .column:first-child {
        margin-left: -4px;
      }
      .column:last-child {
        margin-right: -4px;
      }


      .cards>*,
      .grid>* {
        display: block;
        margin: 4px 4px 8px;
      }
      .cards>*:first-child {
        margin-top: 8px;
      }
      .cards>*:last-child {
        margin-bottom: 4px;
      }

      #staging:not(.grid) {
        visibility: hidden;
        height: 0;
      }
      #staging.grid {
        margin: 0 -4px;
      }
    `}get _cardModder(){return{target:this}}}if(!customElements.get("layout-card")){customElements.define("layout-card",m);const t=n(0);console.info(`%cLAYOUT-CARD ${t.version} IS INSTALLED`,"color: green; font-weight: bold","")}}]);