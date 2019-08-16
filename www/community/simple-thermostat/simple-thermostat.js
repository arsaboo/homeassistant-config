!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define(e):(t=t||self).SimpleThermostat=e()}(this,function(){"use strict";const t=new WeakMap,e=e=>"function"==typeof e&&t.has(e),s=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,i=(t,e,s=null)=>{let i=e;for(;i!==s;){const e=i.nextSibling;t.removeChild(i),i=e}},n={},r={},o=`{{lit-${String(Math.random()).slice(2)}}}`,a=`\x3c!--${o}--\x3e`,l=new RegExp(`${o}|${a}`),c="$lit$";class h{constructor(t,e){this.parts=[],this.element=e;let s=-1,i=0;const n=[],r=e=>{const a=e.content,h=document.createTreeWalker(a,133,null,!1);let d=0;for(;h.nextNode();){s++;const e=h.currentNode;if(1===e.nodeType){if(e.hasAttributes()){const n=e.attributes;let r=0;for(let t=0;t<n.length;t++)n[t].value.indexOf(o)>=0&&r++;for(;r-- >0;){const n=t.strings[i],r=u.exec(n)[2],o=r.toLowerCase()+c,a=e.getAttribute(o).split(l);this.parts.push({type:"attribute",index:s,name:r,strings:a}),e.removeAttribute(o),i+=a.length-1}}"TEMPLATE"===e.tagName&&r(e)}else if(3===e.nodeType){const t=e.data;if(t.indexOf(o)>=0){const r=e.parentNode,o=t.split(l),a=o.length-1;for(let t=0;t<a;t++)r.insertBefore(""===o[t]?p():document.createTextNode(o[t]),e),this.parts.push({type:"node",index:++s});""===o[a]?(r.insertBefore(p(),e),n.push(e)):e.data=o[a],i+=a}}else if(8===e.nodeType)if(e.data===o){const t=e.parentNode;null!==e.previousSibling&&s!==d||(s++,t.insertBefore(p(),e)),d=s,this.parts.push({type:"node",index:s}),null===e.nextSibling?e.data="":(n.push(e),s--),i++}else{let t=-1;for(;-1!==(t=e.data.indexOf(o,t+1));)this.parts.push({type:"node",index:-1})}}};r(e);for(const t of n)t.parentNode.removeChild(t)}}const d=t=>-1!==t.index,p=()=>document.createComment(""),u=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=\/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;class m{constructor(t,e,s){this._parts=[],this.template=t,this.processor=e,this.options=s}update(t){let e=0;for(const s of this._parts)void 0!==s&&s.setValue(t[e]),e++;for(const t of this._parts)void 0!==t&&t.commit()}_clone(){const t=s?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),e=this.template.parts;let i=0,n=0;const r=t=>{const s=document.createTreeWalker(t,133,null,!1);let o=s.nextNode();for(;i<e.length&&null!==o;){const t=e[i];if(d(t))if(n===t.index){if("node"===t.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(o.previousSibling),this._parts.push(t)}else this._parts.push(...this.processor.handleAttributeExpressions(o,t.name,t.strings,this.options));i++}else n++,"TEMPLATE"===o.nodeName&&r(o.content),o=s.nextNode();else this._parts.push(void 0),i++}};return r(t),s&&(document.adoptNode(t),customElements.upgrade(t)),t}}class f{constructor(t,e,s,i){this.strings=t,this.values=e,this.type=s,this.processor=i}getHTML(){const t=this.strings.length-1;let e="";for(let s=0;s<t;s++){const t=this.strings[s],i=u.exec(t);e+=i?t.substr(0,i.index)+i[1]+i[2]+c+i[3]+o:t+a}return e+this.strings[t]}getTemplateElement(){const t=document.createElement("template");return t.innerHTML=this.getHTML(),t}}const _=t=>null===t||!("object"==typeof t||"function"==typeof t);class g{constructor(t,e,s){this.dirty=!0,this.element=t,this.name=e,this.strings=s,this.parts=[];for(let t=0;t<s.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new y(this)}_getValue(){const t=this.strings,e=t.length-1;let s="";for(let i=0;i<e;i++){s+=t[i];const e=this.parts[i];if(void 0!==e){const t=e.value;if(null!=t&&(Array.isArray(t)||"string"!=typeof t&&t[Symbol.iterator]))for(const e of t)s+="string"==typeof e?e:String(e);else s+="string"==typeof t?t:String(t)}}return s+=t[e]}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class y{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===n||_(t)&&t===this.value||(this.value=t,e(t)||(this.committer.dirty=!0))}commit(){for(;e(this.value);){const t=this.value;this.value=n,t(this)}this.value!==n&&this.committer.commit()}}class v{constructor(t){this.value=void 0,this._pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(p()),this.endNode=t.appendChild(p())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t._insert(this.startNode=p()),t._insert(this.endNode=p())}insertAfterPart(t){t._insert(this.startNode=p()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this._pendingValue=t}commit(){for(;e(this._pendingValue);){const t=this._pendingValue;this._pendingValue=n,t(this)}const t=this._pendingValue;t!==n&&(_(t)?t!==this.value&&this._commitText(t):t instanceof f?this._commitTemplateResult(t):t instanceof Node?this._commitNode(t):Array.isArray(t)||t[Symbol.iterator]?this._commitIterable(t):t===r?(this.value=r,this.clear()):this._commitText(t))}_insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}_commitNode(t){this.value!==t&&(this.clear(),this._insert(t),this.value=t)}_commitText(t){const e=this.startNode.nextSibling;t=null==t?"":t,e===this.endNode.previousSibling&&3===e.nodeType?e.data=t:this._commitNode(document.createTextNode("string"==typeof t?t:String(t))),this.value=t}_commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value instanceof m&&this.value.template===e)this.value.update(t.values);else{const s=new m(e,t.processor,this.options),i=s._clone();s.update(t.values),this._commitNode(i),this.value=s}}_commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let s,i=0;for(const n of t)void 0===(s=e[i])&&(s=new v(this.options),e.push(s),0===i?s.appendIntoPart(this):s.insertAfterPart(e[i-1])),s.setValue(n),s.commit(),i++;i<e.length&&(e.length=i,this.clear(s&&s.endNode))}clear(t=this.startNode){i(this.startNode.parentNode,t.nextSibling,this.endNode)}}class S{constructor(t,e,s){if(this.value=void 0,this._pendingValue=void 0,2!==s.length||""!==s[0]||""!==s[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=s}setValue(t){this._pendingValue=t}commit(){for(;e(this._pendingValue);){const t=this._pendingValue;this._pendingValue=n,t(this)}if(this._pendingValue===n)return;const t=!!this._pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)),this.value=t,this._pendingValue=n}}class b extends g{constructor(t,e,s){super(t,e,s),this.single=2===s.length&&""===s[0]&&""===s[1]}_createPart(){return new w(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class w extends y{}let x=!1;try{const t={get capture(){return x=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}class P{constructor(t,e,s){this.value=void 0,this._pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=s,this._boundHandleEvent=(t=>this.handleEvent(t))}setValue(t){this._pendingValue=t}commit(){for(;e(this._pendingValue);){const t=this._pendingValue;this._pendingValue=n,t(this)}if(this._pendingValue===n)return;const t=this._pendingValue,s=this.value,i=null==t||null!=s&&(t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive),r=null!=t&&(null==s||i);i&&this.element.removeEventListener(this.eventName,this._boundHandleEvent,this._options),r&&(this._options=C(t),this.element.addEventListener(this.eventName,this._boundHandleEvent,this._options)),this.value=t,this._pendingValue=n}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const C=t=>t&&(x?{capture:t.capture,passive:t.passive,once:t.once}:t.capture);const T=new class{handleAttributeExpressions(t,e,s,i){const n=e[0];return"."===n?new b(t,e.slice(1),s).parts:"@"===n?[new P(t,e.slice(1),i.eventContext)]:"?"===n?[new S(t,e.slice(1),s)]:new g(t,e,s).parts}handleTextExpression(t){return new v(t)}};function N(t){let e=$.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},$.set(t.type,e));let s=e.stringsArray.get(t.strings);if(void 0!==s)return s;const i=t.strings.join(o);return void 0===(s=e.keyString.get(i))&&(s=new h(t,t.getTemplateElement()),e.keyString.set(i,s)),e.stringsArray.set(t.strings,s),s}const $=new Map,A=new WeakMap;(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.0.0");const E=(t,...e)=>new f(t,e,"html",T),z=133;function V(t,e){const{element:{content:s},parts:i}=t,n=document.createTreeWalker(s,z,null,!1);let r=O(i),o=i[r],a=-1,l=0;const c=[];let h=null;for(;n.nextNode();){a++;const t=n.currentNode;for(t.previousSibling===h&&(h=null),e.has(t)&&(c.push(t),null===h&&(h=t)),null!==h&&l++;void 0!==o&&o.index===a;)o.index=null!==h?-1:o.index-l,o=i[r=O(i,r)]}c.forEach(t=>t.parentNode.removeChild(t))}const k=t=>{let e=11===t.nodeType?0:1;const s=document.createTreeWalker(t,z,null,!1);for(;s.nextNode();)e++;return e},O=(t,e=-1)=>{for(let s=e+1;s<t.length;s++){const e=t[s];if(d(e))return s}return-1};const j=(t,e)=>`${t}--${e}`;let M=!0;void 0===window.ShadyCSS?M=!1:void 0===window.ShadyCSS.prepareTemplateDom&&(console.warn("Incompatible ShadyCSS version detected.Please update to at least @webcomponents/webcomponentsjs@2.0.2 and@webcomponents/shadycss@1.3.1."),M=!1);const R=t=>e=>{const s=j(e.type,t);let i=$.get(s);void 0===i&&(i={stringsArray:new WeakMap,keyString:new Map},$.set(s,i));let n=i.stringsArray.get(e.strings);if(void 0!==n)return n;const r=e.strings.join(o);if(void 0===(n=i.keyString.get(r))){const s=e.getTemplateElement();M&&window.ShadyCSS.prepareTemplateDom(s,t),n=new h(e,s),i.keyString.set(r,n)}return i.stringsArray.set(e.strings,n),n},U=["html","svg"],I=new Set,q=(t,e,s)=>{I.add(s);const i=t.querySelectorAll("style");if(0===i.length)return void window.ShadyCSS.prepareTemplateStyles(e.element,s);const n=document.createElement("style");for(let t=0;t<i.length;t++){const e=i[t];e.parentNode.removeChild(e),n.textContent+=e.textContent}if((t=>{U.forEach(e=>{const s=$.get(j(e,t));void 0!==s&&s.keyString.forEach(t=>{const{element:{content:e}}=t,s=new Set;Array.from(e.querySelectorAll("style")).forEach(t=>{s.add(t)}),V(t,s)})})})(s),function(t,e,s=null){const{element:{content:i},parts:n}=t;if(null==s)return void i.appendChild(e);const r=document.createTreeWalker(i,z,null,!1);let o=O(n),a=0,l=-1;for(;r.nextNode();)for(l++,r.currentNode===s&&(a=k(e),s.parentNode.insertBefore(e,s));-1!==o&&n[o].index===l;){if(a>0){for(;-1!==o;)n[o].index+=a,o=O(n,o);return}o=O(n,o)}}(e,n,e.element.content.firstChild),window.ShadyCSS.prepareTemplateStyles(e.element,s),window.ShadyCSS.nativeShadow){const s=e.element.content.querySelector("style");t.insertBefore(s.cloneNode(!0),t.firstChild)}else{e.element.content.insertBefore(n,e.element.content.firstChild);const t=new Set;t.add(n),V(e,t)}};window.JSCompiler_renameProperty=((t,e)=>t);const F={toAttribute(t,e){switch(e){case Boolean:return t?"":null;case Object:case Array:return null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){switch(e){case Boolean:return null!==t;case Number:return null===t?null:Number(t);case Object:case Array:return JSON.parse(t)}return t}},H=(t,e)=>e!==t&&(e==e||t==t),L={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:H},B=Promise.resolve(!0),W=1,J=4,D=8,K=16,Y=32;class G extends HTMLElement{constructor(){super(),this._updateState=0,this._instanceProperties=void 0,this._updatePromise=B,this._hasConnectedResolver=void 0,this._changedProperties=new Map,this._reflectingProperties=void 0,this.initialize()}static get observedAttributes(){this.finalize();const t=[];return this._classProperties.forEach((e,s)=>{const i=this._attributeNameForProperty(s,e);void 0!==i&&(this._attributeToPropertyMap.set(i,s),t.push(i))}),t}static _ensureClassProperties(){if(!this.hasOwnProperty(JSCompiler_renameProperty("_classProperties",this))){this._classProperties=new Map;const t=Object.getPrototypeOf(this)._classProperties;void 0!==t&&t.forEach((t,e)=>this._classProperties.set(e,t))}}static createProperty(t,e=L){if(this._ensureClassProperties(),this._classProperties.set(t,e),e.noAccessor||this.prototype.hasOwnProperty(t))return;const s="symbol"==typeof t?Symbol():`__${t}`;Object.defineProperty(this.prototype,t,{get(){return this[s]},set(e){const i=this[t];this[s]=e,this._requestUpdate(t,i)},configurable:!0,enumerable:!0})}static finalize(){if(this.hasOwnProperty(JSCompiler_renameProperty("finalized",this))&&this.finalized)return;const t=Object.getPrototypeOf(this);if("function"==typeof t.finalize&&t.finalize(),this.finalized=!0,this._ensureClassProperties(),this._attributeToPropertyMap=new Map,this.hasOwnProperty(JSCompiler_renameProperty("properties",this))){const t=this.properties,e=[...Object.getOwnPropertyNames(t),..."function"==typeof Object.getOwnPropertySymbols?Object.getOwnPropertySymbols(t):[]];for(const s of e)this.createProperty(s,t[s])}}static _attributeNameForProperty(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}static _valueHasChanged(t,e,s=H){return s(t,e)}static _propertyValueFromAttribute(t,e){const s=e.type,i=e.converter||F,n="function"==typeof i?i:i.fromAttribute;return n?n(t,s):t}static _propertyValueToAttribute(t,e){if(void 0===e.reflect)return;const s=e.type,i=e.converter;return(i&&i.toAttribute||F.toAttribute)(t,s)}initialize(){this._saveInstanceProperties(),this._requestUpdate()}_saveInstanceProperties(){this.constructor._classProperties.forEach((t,e)=>{if(this.hasOwnProperty(e)){const t=this[e];delete this[e],this._instanceProperties||(this._instanceProperties=new Map),this._instanceProperties.set(e,t)}})}_applyInstanceProperties(){this._instanceProperties.forEach((t,e)=>this[e]=t),this._instanceProperties=void 0}connectedCallback(){this._updateState=this._updateState|Y,this._hasConnectedResolver&&(this._hasConnectedResolver(),this._hasConnectedResolver=void 0)}disconnectedCallback(){}attributeChangedCallback(t,e,s){e!==s&&this._attributeToProperty(t,s)}_propertyToAttribute(t,e,s=L){const i=this.constructor,n=i._attributeNameForProperty(t,s);if(void 0!==n){const t=i._propertyValueToAttribute(e,s);if(void 0===t)return;this._updateState=this._updateState|D,null==t?this.removeAttribute(n):this.setAttribute(n,t),this._updateState=this._updateState&~D}}_attributeToProperty(t,e){if(this._updateState&D)return;const s=this.constructor,i=s._attributeToPropertyMap.get(t);if(void 0!==i){const t=s._classProperties.get(i)||L;this._updateState=this._updateState|K,this[i]=s._propertyValueFromAttribute(e,t),this._updateState=this._updateState&~K}}_requestUpdate(t,e){let s=!0;if(void 0!==t){const i=this.constructor,n=i._classProperties.get(t)||L;i._valueHasChanged(this[t],e,n.hasChanged)?(this._changedProperties.has(t)||this._changedProperties.set(t,e),!0!==n.reflect||this._updateState&K||(void 0===this._reflectingProperties&&(this._reflectingProperties=new Map),this._reflectingProperties.set(t,n))):s=!1}!this._hasRequestedUpdate&&s&&this._enqueueUpdate()}requestUpdate(t,e){return this._requestUpdate(t,e),this.updateComplete}async _enqueueUpdate(){let t,e;this._updateState=this._updateState|J;const s=this._updatePromise;this._updatePromise=new Promise((s,i)=>{t=s,e=i});try{await s}catch(t){}this._hasConnected||await new Promise(t=>this._hasConnectedResolver=t);try{const t=this.performUpdate();null!=t&&await t}catch(t){e(t)}t(!this._hasRequestedUpdate)}get _hasConnected(){return this._updateState&Y}get _hasRequestedUpdate(){return this._updateState&J}get hasUpdated(){return this._updateState&W}performUpdate(){this._instanceProperties&&this._applyInstanceProperties();let t=!1;const e=this._changedProperties;try{(t=this.shouldUpdate(e))&&this.update(e)}catch(e){throw t=!1,e}finally{this._markUpdated()}t&&(this._updateState&W||(this._updateState=this._updateState|W,this.firstUpdated(e)),this.updated(e))}_markUpdated(){this._changedProperties=new Map,this._updateState=this._updateState&~J}get updateComplete(){return this._updatePromise}shouldUpdate(t){return!0}update(t){void 0!==this._reflectingProperties&&this._reflectingProperties.size>0&&(this._reflectingProperties.forEach((t,e)=>this._propertyToAttribute(e,this[e],t)),this._reflectingProperties=void 0)}updated(t){}firstUpdated(t){}}G.finalized=!0;const Q="adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,X=Symbol();class Z{constructor(t,e){if(e!==X)throw new Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){return void 0===this._styleSheet&&(Q?(this._styleSheet=new CSSStyleSheet,this._styleSheet.replaceSync(this.cssText)):this._styleSheet=null),this._styleSheet}toString(){return this.cssText}}(window.litElementVersions||(window.litElementVersions=[])).push("2.0.1");const tt=t=>t.flat?t.flat(1/0):function t(e,s=[]){for(let i=0,n=e.length;i<n;i++){const n=e[i];Array.isArray(n)?t(n,s):s.push(n)}return s}(t);class et extends G{static finalize(){super.finalize(),this._styles=this.hasOwnProperty(JSCompiler_renameProperty("styles",this))?this._getUniqueStyles():this._styles||[]}static _getUniqueStyles(){const t=this.styles,e=[];if(Array.isArray(t)){tt(t).reduceRight((t,e)=>(t.add(e),t),new Set).forEach(t=>e.unshift(t))}else t&&e.push(t);return e}initialize(){super.initialize(),this.renderRoot=this.createRenderRoot(),window.ShadowRoot&&this.renderRoot instanceof window.ShadowRoot&&this.adoptStyles()}createRenderRoot(){return this.attachShadow({mode:"open"})}adoptStyles(){const t=this.constructor._styles;0!==t.length&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow?Q?this.renderRoot.adoptedStyleSheets=t.map(t=>t.styleSheet):this._needsShimAdoptedStyleSheets=!0:window.ShadyCSS.ScopingShim.prepareAdoptedCssText(t.map(t=>t.cssText),this.localName))}connectedCallback(){super.connectedCallback(),this.hasUpdated&&void 0!==window.ShadyCSS&&window.ShadyCSS.styleElement(this)}update(t){super.update(t);const e=this.render();e instanceof f&&this.constructor.render(e,this.renderRoot,{scopeName:this.localName,eventContext:this}),this._needsShimAdoptedStyleSheets&&(this._needsShimAdoptedStyleSheets=!1,this.constructor._styles.forEach(t=>{const e=document.createElement("style");e.textContent=t.cssText,this.renderRoot.appendChild(e)}))}render(){}}et.finalized=!0,et.render=((t,e,s)=>{const n=s.scopeName,r=A.has(e),o=e instanceof ShadowRoot&&M&&t instanceof f,a=o&&!I.has(n),l=a?document.createDocumentFragment():e;if(((t,e,s)=>{let n=A.get(e);void 0===n&&(i(e,e.firstChild),A.set(e,n=new v(Object.assign({templateFactory:N},s))),n.appendInto(e)),n.setValue(t),n.commit()})(t,l,Object.assign({templateFactory:R(n)},s)),a){const t=A.get(l);A.delete(l),t.value instanceof m&&q(l,t.value.template,n),i(e,e.firstChild),e.appendChild(l),A.set(e,t)}!r&&o&&window.ShadyCSS.styleElement(e.host)});const st=(t,e)=>{for(const s of Reflect.ownKeys(e))Object.defineProperty(t,s,Object.getOwnPropertyDescriptor(e,s));return t};var it=st,nt=st;it.default=nt;var rt=(t,e={})=>{if("function"!=typeof t)throw new TypeError(`Expected the first argument to be a function, got \`${typeof t}\``);let s,i;const n=function(...n){const r=this,o=e.immediate&&!s;return clearTimeout(s),s=setTimeout(()=>{s=null,e.immediate||(i=t.apply(r,n))},e.wait||0),o&&(i=t.apply(r,n)),i};return it(n,t),n.cancel=(()=>{s&&(clearTimeout(s),s=null)}),n},ot=((t,...e)=>{const s=e.reduce((e,s,i)=>e+(t=>{if(t instanceof Z)return t.cssText;throw new Error(`Value passed to 'css' function must be a 'css' function result: ${t}. Use 'unsafeCSS' to pass non-literal values, but\n            take care to ensure page security.`)})(s)+t[i+1],t[0]);return new Z(s,X)})`
  :host {
    --st-font-size-xl: var(--paper-font-display3_-_font-size);
    --st-font-size-l: var(--paper-font-display2_-_font-size);
    --st-font-size-m: var(--paper-font-title_-_font-size);
    --st-font-size-title: var(--ha-card-header-font-size, 24px);
    --st-font-size-sensors: var(--paper-font-subhead_-_font-size, 16px);
    --st-spacing: 4px;
  }

  ha-card {
    -webkit-font-smoothing: var(
      --paper-font-body1_-_-webkit-font-smoothing
    );
    font-size: var(--paper-font-body1_-_font-size);
    font-weight: var(--paper-font-body1_-_font-weight);
    line-height: var(--paper-font-body1_-_line-height);

    padding-bottom: calc(var(--st-spacing) * 4);
  }

  ha-card.no-header {
    padding: calc(var(--st-spacing) * 4) 0;
  }

  .not-found {
    flex: 1;
    background-color: yellow;
    padding: calc(var(--st-spacing) * 4);
  }

  .body {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
  }
  .main {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
  }
  .sensors {
    font-size: var(--st-font-size-sensors);
  }
  table:empty {
    display: none;
  }
  header {
    display: flex;
    flex-direction: row;
    align-items: center;

    padding: calc(var(--st-spacing) * 6)
      calc(var(--st-spacing) * 4)
      calc(var(--st-spacing) * 4);
  }
  .header__icon {
    margin-right: calc(var(--st-spacing) * 2);
    color: var(--paper-item-icon-color, #44739e);
  }
  .header__title {
    font-size: var(--st-font-size-title);
    line-height: var(--st-font-size-title);
    -webkit-font-smoothing: var(
      --paper-font-headline_-_-webkit-font-smoothing
    );
    font-weight: normal;
    margin: 0;
    align-self: left;
  }
  .current-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .current--value {
    margin: 0;
    font-size: var(--st-font-size-xl);
    font-weight: 400;
    line-height: var(--st-font-size-xl);
  }
  .current--unit {
    font-size: var(--st-font-size-m);
  }
  .thermostat-trigger {
    padding: 0px;
  }
  .sensors th {
    text-align: right;
    font-weight: 300;
    padding-right: 8px;
    padding-bottom: 4px;
  }
  .sensors td {
    padding-bottom: 4px;
  }
  .clickable {
    cursor: pointer;
  }
  .modes {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    padding-left: calc(var(--st-spacing) * 4);
    padding-right: calc(var(--st-spacing) * 4);
  }
  .mode--active {
    color: var(--paper-item-icon-color, #44739e);
  }
  .mode__icon {
    padding-right: var(--st-spacing);
  }
`;function at(t,{decimals:e=1,fallback:s="N/A"}={}){if(null===t||""===t||["boolean","undefined"].includes(typeof t))return s;const[i,n]=String(t).split(".");return Number.isNaN(i)?s:e?`${i}.${Math.round(n)||"0"}`:String(Math.round(t))}const lt="dual",ct="single";const ht=["operation","fan"],dt=1e3,pt=.5,ut=1,mt=["entity","sensors","_values"],ft={auto:"hass:autorenew",manual:"hass:cursor-pointer",heat:"hass:fire",cool:"hass:snowflake",off:"hass:power",fan_only:"hass:fan",fan:"hass:fan",eco:"hass:leaf",dry:"hass:water-percent",idle:"hass:power"},_t={off:"mdi:radiator-off",on:"mdi:radiator",idle:"mdi:radiator-disabled",heat:"mdi:radiator",cool:"mdi:snowflake",auto:"mdi:radiator",manual:"mdi:radiator",boost:"mdi:fire",away:"mdi:radiator-disabled"},gt={temperature:!1,state:!1,mode:!1,away:!0};class yt extends et{static get styles(){return ot}static get properties(){return{_hass:Object,config:Object,entity:Object,sensors:Array,modeType:String,modes:Object,icon:String,_values:Object,_mode:String,_hide:Object,name:String}}constructor(){super(),this._debouncedSetTemperature=rt(t=>{this._hass.callService("climate","set_temperature",{entity_id:this.config.entity,...t})},{wait:dt}),this._hass=null,this.entity=null,this.icon=null,this.sensors=[],this._stepSize=pt,this._values={},this._mode=null,this._hide=gt,this._haVersion=null,this.modeType="operation"}setConfig(t){if(!t.entity)throw new Error("You need to define an entity");t.mode_type&&ht.includes(t.mode_type)&&(this.modeType=t.mode_type),this.config={decimals:ut,...t}}set hass(t){this._hass=t;const e=t.states[this.config.entity];if(void 0===e)return;this._haVersion=t.config.version.split(".").map(t=>parseInt(t,10));const{attributes:{[`${this.modeType}_mode`]:s,[`${this.modeType}_list`]:i=[],...n}}=e;if(this.entityType=function(t){return"number"==typeof t.target_temp_high&&"number"==typeof t.target_temp_low?lt:ct}(n),"dual"===this.entityType?this._values={target_temp_low:n.target_temp_low,target_temp_high:n.target_temp_high}:this._values={temperature:n.temperature},this.entity!==e){this.entity=e,this._mode=s,this.modes={};for(const t of i)this.modes[t]={include:!0,icon:ft[t]}}!1===this.config.modes?this.modes=!1:"object"==typeof this.config.modes&&Object.entries(this.config.modes).map(([t,e])=>{this.modes.hasOwnProperty(t)&&("boolean"==typeof e?this.modes[t].include=e:this.modes[t]={...this.modes[t],...e})}),void 0!==this.config.icon?this.icon=this.config.icon:this.icon=_t,this.config.step_size&&(this._stepSize=this.config.step_size),this.config.hide&&(this._hide={...this._hide,...this.config.hide}),"string"==typeof this.config.name?this.name=this.config.name:!1===this.config.name?this.name=!1:this.name=e.attributes.friendly_name,this.config.sensors&&(this.sensors=this.config.sensors.map(({name:e,entity:s,attribute:i,unit:n="",...r})=>{let o;const a=[e];return s?(o=t.states[s],a.push(o&&o.attributes&&o.attributes.friendly_name),i&&(o=o.attributes[i]+n)):i&&i in this.entity.attributes&&(o=this.entity.attributes[i]+n,a.push(i)),a.push(s),{...r,name:a.find(t=>!!t),state:o,entity:s}}))}shouldUpdate(t){return mt.some(e=>t.has(e))}localize(t,e=""){const s=this._hass.selectedLanguage||this._hass.language,i=`${e}${t}`,n=this._hass.resources[s];return i in n?n[i]:t}render({_hass:t,_hide:e,_values:s,config:i,entity:n,sensors:r}=this){if(!n)return E`
        <ha-card class="not-found">
          Entity not available: <strong class="name">${i.entity}</strong>
        </ha-card>
      `;const{state:o,attributes:{min_temp:a=null,max_temp:l=null,current_temperature:c,[`${this.modeType}_mode`]:h,...d}}=n,p=this._hass.config.unit_system.temperature,u=[e.temperature?null:this.renderInfoItem(`${at(c,i)}${p}`,{heading:"Temperature"}),e.state?null:this.renderInfoItem(this.localize(o,"state.climate."),{heading:"State"}),e.away?null:this.renderAwayToggle(d.away_mode),r.map(({name:t,icon:e,state:s})=>s&&this.renderInfoItem(s,{heading:t,icon:e}))||null].filter(t=>null!==t);return E`
      <ha-card class="${this.name?"":"no-header"}">
        ${this.renderHeader()}
        <section class="body">
          <table class="sensors">
            ${u}
          </table>

          ${Object.entries(s).map(([t,e])=>E`
              <div class="main">
                <div class="current-wrapper">
                  <paper-icon-button
                    ?disabled=${l&&e>=l}
                    class="thermostat-trigger"
                    icon="hass:chevron-up"
                    @click="${()=>this.setTemperature(this._stepSize,t)}"
                  >
                  </paper-icon-button>

                  <div @click=${()=>this.openEntityPopover()}>
                    <h3 class="current--value">
                      ${at(e,i)}
                    </h3>
                  </div>
                  <paper-icon-button
                    ?disabled=${a&&e<=a}
                    class="thermostat-trigger"
                    icon="hass:chevron-down"
                    @click="${()=>this.setTemperature(-this._stepSize,t)}"
                  >
                  </paper-icon-button>
                </div>
                <span class="current--unit">${p}</span>
              </div>
            `)}
        </section>
        ${this.renderModeSelector(h)}
      </ha-card>
    `}renderHeader(){if(!1===this.name)return"";let t=this.icon;const{state:e}=this.entity;return"object"==typeof this.icon&&(t=e in this.icon&&this.icon[e]),E`
      <header class="clickable" @click=${()=>this.openEntityPopover()}>
        ${t&&E`
            <ha-icon class="header__icon" .icon=${t}></ha-icon>
          `||""}
        <h2 class="header__title">${this.name}</h2>
      </header>
    `}renderModeSelector(t){if(!1===this.modes)return;const e=Object.entries(this.modes).filter(([t,e])=>e.include),s=(t,e)=>!1===e.name?null:e.name||this.localize(t,"state.climate."),i=t=>!1===t?null:E`
        <ha-icon class="mode__icon" .icon=${t}></ha-icon>
      `;return this._haVersion[1]<=87?E`
        <div class="modes">
          ${e.map(([e,n])=>E`
              <paper-button
                class="${e===t?"mode--active":""}"
                @click=${()=>this.setMode(e)}
              >
                ${i(n.icon)} ${s(e,n)}
              </paper-button>
            `)}
        </div>
      `:E`
      <div class="modes">
        ${e.map(([e,n])=>E`
            <mwc-button
              ?disabled=${e===t}
              ?outlined=${e===t}
              ?dense=${!0}
              @click=${()=>this.setMode(e)}
            >
              ${i(n.icon)} ${s(e,n)}
            </mwc-button>
          `)}
      </div>
    `}renderAwayToggle(t){return E`
      <tr>
        <th>${this.localize("ui.card.climate.away_mode")}</th>
        <td>
          <paper-toggle-button
            ?checked=${"on"===t}
            @click=${()=>{this._hass.callService("climate","set_away_mode",{entity_id:this.config.entity,away_mode:!("on"===t)})}}
          />
        </td>
      </tr>
    `}renderInfoItem(t,{heading:e,icon:s}){if(!t)return;let i,n;if("object"==typeof t){let e=t.state;if("device_class"in t.attributes){const[s]=t.entity_id.split("."),i=["state",s,t.attributes.device_class,""].join(".");e=this.localize(t.state,i)}i=E`
        <td
          class="clickable"
          @click="${()=>this.openEntityPopover(t.entity_id)}"
        >
          ${e} ${t.attributes.unit_of_measurement}
        </td>
      `}else i=E`
        <td>${t}</td>
      `;return n=s?E`
        <th><ha-icon icon="${s}"></ha-icon></th>
      `:E`
        <th>${e}:</th>
      `,E`
      <tr>
        ${n} ${i}
      </tr>
    `}setTemperature(t,e="temperature"){this._values={...this._values,[e]:this._values[e]+t},this._debouncedSetTemperature({...this._values})}setMode(t){t&&t!==this._mode&&this._hass.callService("climate",`set_${this.modeType}_mode`,{entity_id:this.config.entity,[`${this.modeType}_mode`]:t})}openEntityPopover(t=this.config.entity){this.fire("hass-more-info",{entityId:t})}fire(t,e,s){s=s||{},e=null==e?{}:e;const i=new Event(t,{bubbles:void 0===s.bubbles||s.bubbles,cancelable:Boolean(s.cancelable),composed:void 0===s.composed||s.composed});return i.detail=e,this.dispatchEvent(i),i}getCardSize(){return 3}}return window.customElements.define("simple-thermostat",yt),yt});
