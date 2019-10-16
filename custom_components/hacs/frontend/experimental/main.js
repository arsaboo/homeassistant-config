/*! *****************************************************************************
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
MERCHANTABLITY OR NON-INFRINGEMENT.

See the Apache Version 2.0 License for specific language governing permissions
and limitations under the License.
***************************************************************************** */
function t(t,e,o,s){var i,r=arguments.length,a=r<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,o):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(t,e,o,s);else for(var n=t.length-1;n>=0;n--)(i=t[n])&&(a=(r<3?i(a):r>3?i(e,o,a):i(e,o))||a);return r>3&&a&&Object.defineProperty(e,o,a),a
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */}const e=new WeakMap,o=t=>"function"==typeof t&&e.has(t),s=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,i=(t,e,o=null)=>{for(;e!==o;){const o=e.nextSibling;t.removeChild(e),e=o}},r={},a={},n=`{{lit-${String(Math.random()).slice(2)}}}`,p=`\x3c!--${n}--\x3e`,c=new RegExp(`${n}|${p}`),l="$lit$";class h{constructor(t,e){this.parts=[],this.element=e;const o=[],s=[],i=document.createTreeWalker(e.content,133,null,!1);let r=0,a=-1,p=0;const{strings:h,values:{length:u}}=t;for(;p<u;){const t=i.nextNode();if(null!==t){if(a++,1===t.nodeType){if(t.hasAttributes()){const e=t.attributes,{length:o}=e;let s=0;for(let t=0;t<o;t++)d(e[t].name,l)&&s++;for(;s-- >0;){const e=h[p],o=y.exec(e)[2],s=o.toLowerCase()+l,i=t.getAttribute(s);t.removeAttribute(s);const r=i.split(c);this.parts.push({type:"attribute",index:a,name:o,strings:r}),p+=r.length-1}}"TEMPLATE"===t.tagName&&(s.push(t),i.currentNode=t.content)}else if(3===t.nodeType){const e=t.data;if(e.indexOf(n)>=0){const s=t.parentNode,i=e.split(c),r=i.length-1;for(let e=0;e<r;e++){let o,r=i[e];if(""===r)o=m();else{const t=y.exec(r);null!==t&&d(t[2],l)&&(r=r.slice(0,t.index)+t[1]+t[2].slice(0,-l.length)+t[3]),o=document.createTextNode(r)}s.insertBefore(o,t),this.parts.push({type:"node",index:++a})}""===i[r]?(s.insertBefore(m(),t),o.push(t)):t.data=i[r],p+=r}}else if(8===t.nodeType)if(t.data===n){const e=t.parentNode;null!==t.previousSibling&&a!==r||(a++,e.insertBefore(m(),t)),r=a,this.parts.push({type:"node",index:a}),null===t.nextSibling?t.data="":(o.push(t),a--),p++}else{let e=-1;for(;-1!==(e=t.data.indexOf(n,e+1));)this.parts.push({type:"node",index:-1}),p++}}else i.currentNode=s.pop()}for(const t of o)t.parentNode.removeChild(t)}}const d=(t,e)=>{const o=t.length-e.length;return o>=0&&t.slice(o)===e},u=t=>-1!==t.index,m=()=>document.createComment(""),y=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F "'>=/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
class g{constructor(t,e,o){this.__parts=[],this.template=t,this.processor=e,this.options=o}update(t){let e=0;for(const o of this.__parts)void 0!==o&&o.setValue(t[e]),e++;for(const t of this.__parts)void 0!==t&&t.commit()}_clone(){const t=s?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),e=[],o=this.template.parts,i=document.createTreeWalker(t,133,null,!1);let r,a=0,n=0,p=i.nextNode();for(;a<o.length;)if(r=o[a],u(r)){for(;n<r.index;)n++,"TEMPLATE"===p.nodeName&&(e.push(p),i.currentNode=p.content),null===(p=i.nextNode())&&(i.currentNode=e.pop(),p=i.nextNode());if("node"===r.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(p.previousSibling),this.__parts.push(t)}else this.__parts.push(...this.processor.handleAttributeExpressions(p,r.name,r.strings,this.options));a++}else this.__parts.push(void 0),a++;return s&&(document.adoptNode(t),customElements.upgrade(t)),t}}
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const v=` ${n} `;class f{constructor(t,e,o,s){this.strings=t,this.values=e,this.type=o,this.processor=s}getHTML(){const t=this.strings.length-1;let e="",o=!1;for(let s=0;s<t;s++){const t=this.strings[s],i=t.lastIndexOf("\x3c!--");o=(i>-1||o)&&-1===t.indexOf("--\x3e",i+1);const r=y.exec(t);e+=null===r?t+(o?v:p):t.substr(0,r.index)+r[1]+r[2]+l+r[3]+n}return e+=this.strings[t]}getTemplateElement(){const t=document.createElement("template");return t.innerHTML=this.getHTML(),t}}
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const _=t=>null===t||!("object"==typeof t||"function"==typeof t),b=t=>Array.isArray(t)||!(!t||!t[Symbol.iterator]);class w{constructor(t,e,o){this.dirty=!0,this.element=t,this.name=e,this.strings=o,this.parts=[];for(let t=0;t<o.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new S(this)}_getValue(){const t=this.strings,e=t.length-1;let o="";for(let s=0;s<e;s++){o+=t[s];const e=this.parts[s];if(void 0!==e){const t=e.value;if(_(t)||!b(t))o+="string"==typeof t?t:String(t);else for(const e of t)o+="string"==typeof e?e:String(e)}}return o+=t[e]}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class S{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===r||_(t)&&t===this.value||(this.value=t,o(t)||(this.committer.dirty=!0))}commit(){for(;o(this.value);){const t=this.value;this.value=r,t(this)}this.value!==r&&this.committer.commit()}}class x{constructor(t){this.value=void 0,this.__pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(m()),this.endNode=t.appendChild(m())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t.__insert(this.startNode=m()),t.__insert(this.endNode=m())}insertAfterPart(t){t.__insert(this.startNode=m()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this.__pendingValue=t}commit(){for(;o(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=r,t(this)}const t=this.__pendingValue;t!==r&&(_(t)?t!==this.value&&this.__commitText(t):t instanceof f?this.__commitTemplateResult(t):t instanceof Node?this.__commitNode(t):b(t)?this.__commitIterable(t):t===a?(this.value=a,this.clear()):this.__commitText(t))}__insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}__commitNode(t){this.value!==t&&(this.clear(),this.__insert(t),this.value=t)}__commitText(t){const e=this.startNode.nextSibling,o="string"==typeof(t=null==t?"":t)?t:String(t);e===this.endNode.previousSibling&&3===e.nodeType?e.data=o:this.__commitNode(document.createTextNode(o)),this.value=t}__commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value instanceof g&&this.value.template===e)this.value.update(t.values);else{const o=new g(e,t.processor,this.options),s=o._clone();o.update(t.values),this.__commitNode(s),this.value=o}}__commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let o,s=0;for(const i of t)void 0===(o=e[s])&&(o=new x(this.options),e.push(o),0===s?o.appendIntoPart(this):o.insertAfterPart(e[s-1])),o.setValue(i),o.commit(),s++;s<e.length&&(e.length=s,this.clear(o&&o.endNode))}clear(t=this.startNode){i(this.startNode.parentNode,t.nextSibling,this.endNode)}}class ${constructor(t,e,o){if(this.value=void 0,this.__pendingValue=void 0,2!==o.length||""!==o[0]||""!==o[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=o}setValue(t){this.__pendingValue=t}commit(){for(;o(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=r,t(this)}if(this.__pendingValue===r)return;const t=!!this.__pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name),this.value=t),this.__pendingValue=r}}class P extends w{constructor(t,e,o){super(t,e,o),this.single=2===o.length&&""===o[0]&&""===o[1]}_createPart(){return new k(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class k extends S{}let A=!1;try{const t={get capture(){return A=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}class C{constructor(t,e,o){this.value=void 0,this.__pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=o,this.__boundHandleEvent=t=>this.handleEvent(t)}setValue(t){this.__pendingValue=t}commit(){for(;o(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=r,t(this)}if(this.__pendingValue===r)return;const t=this.__pendingValue,e=this.value,s=null==t||null!=e&&(t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive),i=null!=t&&(null==e||s);s&&this.element.removeEventListener(this.eventName,this.__boundHandleEvent,this.__options),i&&(this.__options=T(t),this.element.addEventListener(this.eventName,this.__boundHandleEvent,this.__options)),this.value=t,this.__pendingValue=r}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const T=t=>t&&(A?{capture:t.capture,passive:t.passive,once:t.once}:t.capture);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const z=new class{handleAttributeExpressions(t,e,o,s){const i=e[0];if("."===i){return new P(t,e.slice(1),o).parts}return"@"===i?[new C(t,e.slice(1),s.eventContext)]:"?"===i?[new $(t,e.slice(1),o)]:new w(t,e,o).parts}handleTextExpression(t){return new x(t)}};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */function N(t){let e=R.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},R.set(t.type,e));let o=e.stringsArray.get(t.strings);if(void 0!==o)return o;const s=t.strings.join(n);return void 0===(o=e.keyString.get(s))&&(o=new h(t,t.getTemplateElement()),e.keyString.set(s,o)),e.stringsArray.set(t.strings,o),o}const R=new Map,E=new WeakMap;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.1.2");const U=(t,...e)=>new f(t,e,"html",z),V=133;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */function M(t,e){const{element:{content:o},parts:s}=t,i=document.createTreeWalker(o,V,null,!1);let r=q(s),a=s[r],n=-1,p=0;const c=[];let l=null;for(;i.nextNode();){n++;const t=i.currentNode;for(t.previousSibling===l&&(l=null),e.has(t)&&(c.push(t),null===l&&(l=t)),null!==l&&p++;void 0!==a&&a.index===n;)a.index=null!==l?-1:a.index-p,a=s[r=q(s,r)]}c.forEach(t=>t.parentNode.removeChild(t))}const O=t=>{let e=11===t.nodeType?0:1;const o=document.createTreeWalker(t,V,null,!1);for(;o.nextNode();)e++;return e},q=(t,e=-1)=>{for(let o=e+1;o<t.length;o++){const e=t[o];if(u(e))return o}return-1};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const I=(t,e)=>`${t}--${e}`;let L=!0;void 0===window.ShadyCSS?L=!1:void 0===window.ShadyCSS.prepareTemplateDom&&(console.warn("Incompatible ShadyCSS version detected. Please update to at least @webcomponents/webcomponentsjs@2.0.2 and @webcomponents/shadycss@1.3.1."),L=!1);const j=t=>e=>{const o=I(e.type,t);let s=R.get(o);void 0===s&&(s={stringsArray:new WeakMap,keyString:new Map},R.set(o,s));let i=s.stringsArray.get(e.strings);if(void 0!==i)return i;const r=e.strings.join(n);if(void 0===(i=s.keyString.get(r))){const o=e.getTemplateElement();L&&window.ShadyCSS.prepareTemplateDom(o,t),i=new h(e,o),s.keyString.set(r,i)}return s.stringsArray.set(e.strings,i),i},D=["html","svg"],W=new Set,B=(t,e,o)=>{W.add(t);const s=o?o.element:document.createElement("template"),i=e.querySelectorAll("style"),{length:r}=i;if(0===r)return void window.ShadyCSS.prepareTemplateStyles(s,t);const a=document.createElement("style");for(let t=0;t<r;t++){const e=i[t];e.parentNode.removeChild(e),a.textContent+=e.textContent}(t=>{D.forEach(e=>{const o=R.get(I(e,t));void 0!==o&&o.keyString.forEach(t=>{const{element:{content:e}}=t,o=new Set;Array.from(e.querySelectorAll("style")).forEach(t=>{o.add(t)}),M(t,o)})})})(t);const n=s.content;o?function(t,e,o=null){const{element:{content:s},parts:i}=t;if(null==o)return void s.appendChild(e);const r=document.createTreeWalker(s,V,null,!1);let a=q(i),n=0,p=-1;for(;r.nextNode();){for(p++,r.currentNode===o&&(n=O(e),o.parentNode.insertBefore(e,o));-1!==a&&i[a].index===p;){if(n>0){for(;-1!==a;)i[a].index+=n,a=q(i,a);return}a=q(i,a)}}}(o,a,n.firstChild):n.insertBefore(a,n.firstChild),window.ShadyCSS.prepareTemplateStyles(s,t);const p=n.querySelector("style");if(window.ShadyCSS.nativeShadow&&null!==p)e.insertBefore(p.cloneNode(!0),e.firstChild);else if(o){n.insertBefore(a,n.firstChild);const t=new Set;t.add(a),M(o,t)}};window.JSCompiler_renameProperty=(t,e)=>t;const F={toAttribute(t,e){switch(e){case Boolean:return t?"":null;case Object:case Array:return null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){switch(e){case Boolean:return null!==t;case Number:return null===t?null:Number(t);case Object:case Array:return JSON.parse(t)}return t}},H=(t,e)=>e!==t&&(e==e||t==t),J={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:H},G=Promise.resolve(!0),K=1,Q=4,X=8,Y=16,Z=32,tt="finalized";class et extends HTMLElement{constructor(){super(),this._updateState=0,this._instanceProperties=void 0,this._updatePromise=G,this._hasConnectedResolver=void 0,this._changedProperties=new Map,this._reflectingProperties=void 0,this.initialize()}static get observedAttributes(){this.finalize();const t=[];return this._classProperties.forEach((e,o)=>{const s=this._attributeNameForProperty(o,e);void 0!==s&&(this._attributeToPropertyMap.set(s,o),t.push(s))}),t}static _ensureClassProperties(){if(!this.hasOwnProperty(JSCompiler_renameProperty("_classProperties",this))){this._classProperties=new Map;const t=Object.getPrototypeOf(this)._classProperties;void 0!==t&&t.forEach((t,e)=>this._classProperties.set(e,t))}}static createProperty(t,e=J){if(this._ensureClassProperties(),this._classProperties.set(t,e),e.noAccessor||this.prototype.hasOwnProperty(t))return;const o="symbol"==typeof t?Symbol():`__${t}`;Object.defineProperty(this.prototype,t,{get(){return this[o]},set(e){const s=this[t];this[o]=e,this._requestUpdate(t,s)},configurable:!0,enumerable:!0})}static finalize(){const t=Object.getPrototypeOf(this);if(t.hasOwnProperty(tt)||t.finalize(),this[tt]=!0,this._ensureClassProperties(),this._attributeToPropertyMap=new Map,this.hasOwnProperty(JSCompiler_renameProperty("properties",this))){const t=this.properties,e=[...Object.getOwnPropertyNames(t),..."function"==typeof Object.getOwnPropertySymbols?Object.getOwnPropertySymbols(t):[]];for(const o of e)this.createProperty(o,t[o])}}static _attributeNameForProperty(t,e){const o=e.attribute;return!1===o?void 0:"string"==typeof o?o:"string"==typeof t?t.toLowerCase():void 0}static _valueHasChanged(t,e,o=H){return o(t,e)}static _propertyValueFromAttribute(t,e){const o=e.type,s=e.converter||F,i="function"==typeof s?s:s.fromAttribute;return i?i(t,o):t}static _propertyValueToAttribute(t,e){if(void 0===e.reflect)return;const o=e.type,s=e.converter;return(s&&s.toAttribute||F.toAttribute)(t,o)}initialize(){this._saveInstanceProperties(),this._requestUpdate()}_saveInstanceProperties(){this.constructor._classProperties.forEach((t,e)=>{if(this.hasOwnProperty(e)){const t=this[e];delete this[e],this._instanceProperties||(this._instanceProperties=new Map),this._instanceProperties.set(e,t)}})}_applyInstanceProperties(){this._instanceProperties.forEach((t,e)=>this[e]=t),this._instanceProperties=void 0}connectedCallback(){this._updateState=this._updateState|Z,this._hasConnectedResolver&&(this._hasConnectedResolver(),this._hasConnectedResolver=void 0)}disconnectedCallback(){}attributeChangedCallback(t,e,o){e!==o&&this._attributeToProperty(t,o)}_propertyToAttribute(t,e,o=J){const s=this.constructor,i=s._attributeNameForProperty(t,o);if(void 0!==i){const t=s._propertyValueToAttribute(e,o);if(void 0===t)return;this._updateState=this._updateState|X,null==t?this.removeAttribute(i):this.setAttribute(i,t),this._updateState=this._updateState&~X}}_attributeToProperty(t,e){if(this._updateState&X)return;const o=this.constructor,s=o._attributeToPropertyMap.get(t);if(void 0!==s){const t=o._classProperties.get(s)||J;this._updateState=this._updateState|Y,this[s]=o._propertyValueFromAttribute(e,t),this._updateState=this._updateState&~Y}}_requestUpdate(t,e){let o=!0;if(void 0!==t){const s=this.constructor,i=s._classProperties.get(t)||J;s._valueHasChanged(this[t],e,i.hasChanged)?(this._changedProperties.has(t)||this._changedProperties.set(t,e),!0!==i.reflect||this._updateState&Y||(void 0===this._reflectingProperties&&(this._reflectingProperties=new Map),this._reflectingProperties.set(t,i))):o=!1}!this._hasRequestedUpdate&&o&&this._enqueueUpdate()}requestUpdate(t,e){return this._requestUpdate(t,e),this.updateComplete}async _enqueueUpdate(){let t,e;this._updateState=this._updateState|Q;const o=this._updatePromise;this._updatePromise=new Promise((o,s)=>{t=o,e=s});try{await o}catch(t){}this._hasConnected||await new Promise(t=>this._hasConnectedResolver=t);try{const t=this.performUpdate();null!=t&&await t}catch(t){e(t)}t(!this._hasRequestedUpdate)}get _hasConnected(){return this._updateState&Z}get _hasRequestedUpdate(){return this._updateState&Q}get hasUpdated(){return this._updateState&K}performUpdate(){this._instanceProperties&&this._applyInstanceProperties();let t=!1;const e=this._changedProperties;try{(t=this.shouldUpdate(e))&&this.update(e)}catch(e){throw t=!1,e}finally{this._markUpdated()}t&&(this._updateState&K||(this._updateState=this._updateState|K,this.firstUpdated(e)),this.updated(e))}_markUpdated(){this._changedProperties=new Map,this._updateState=this._updateState&~Q}get updateComplete(){return this._getUpdateComplete()}_getUpdateComplete(){return this._updatePromise}shouldUpdate(t){return!0}update(t){void 0!==this._reflectingProperties&&this._reflectingProperties.size>0&&(this._reflectingProperties.forEach((t,e)=>this._propertyToAttribute(e,this[e],t)),this._reflectingProperties=void 0)}updated(t){}firstUpdated(t){}}et[tt]=!0;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const ot=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:o,elements:s}=e;return{kind:o,elements:s,finisher(e){window.customElements.define(t,e)}}})(t,e),st=(t,e)=>"method"!==e.kind||!e.descriptor||"value"in e.descriptor?{kind:"field",key:Symbol(),placement:"own",descriptor:{},initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(o){o.createProperty(e.key,t)}}:Object.assign({},e,{finisher(o){o.createProperty(e.key,t)}}),it=(t,e,o)=>{e.constructor.createProperty(o,t)};function rt(t){return(e,o)=>void 0!==o?it(t,e,o):st(t,e)}
/**
@license
Copyright (c) 2019 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/const at="adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,nt=Symbol();class pt{constructor(t,e){if(e!==nt)throw new Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){return void 0===this._styleSheet&&(at?(this._styleSheet=new CSSStyleSheet,this._styleSheet.replaceSync(this.cssText)):this._styleSheet=null),this._styleSheet}toString(){return this.cssText}}const ct=(t,...e)=>{const o=e.reduce((e,o,s)=>e+(t=>{if(t instanceof pt)return t.cssText;if("number"==typeof t)return t;throw new Error(`Value passed to 'css' function must be a 'css' function result: ${t}. Use 'unsafeCSS' to pass non-literal values, but\n            take care to ensure page security.`)})(o)+t[s+1],t[0]);return new pt(o,nt)};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
(window.litElementVersions||(window.litElementVersions=[])).push("2.2.1");const lt=t=>t.flat?t.flat(1/0):function t(e,o=[]){for(let s=0,i=e.length;s<i;s++){const i=e[s];Array.isArray(i)?t(i,o):o.push(i)}return o}(t);class ht extends et{static finalize(){super.finalize.call(this),this._styles=this.hasOwnProperty(JSCompiler_renameProperty("styles",this))?this._getUniqueStyles():this._styles||[]}static _getUniqueStyles(){const t=this.styles,e=[];if(Array.isArray(t)){lt(t).reduceRight((t,e)=>(t.add(e),t),new Set).forEach(t=>e.unshift(t))}else t&&e.push(t);return e}initialize(){super.initialize(),this.renderRoot=this.createRenderRoot(),window.ShadowRoot&&this.renderRoot instanceof window.ShadowRoot&&this.adoptStyles()}createRenderRoot(){return this.attachShadow({mode:"open"})}adoptStyles(){const t=this.constructor._styles;0!==t.length&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow?at?this.renderRoot.adoptedStyleSheets=t.map(t=>t.styleSheet):this._needsShimAdoptedStyleSheets=!0:window.ShadyCSS.ScopingShim.prepareAdoptedCssText(t.map(t=>t.cssText),this.localName))}connectedCallback(){super.connectedCallback(),this.hasUpdated&&void 0!==window.ShadyCSS&&window.ShadyCSS.styleElement(this)}update(t){super.update(t);const e=this.render();e instanceof f&&this.constructor.render(e,this.renderRoot,{scopeName:this.localName,eventContext:this}),this._needsShimAdoptedStyleSheets&&(this._needsShimAdoptedStyleSheets=!1,this.constructor._styles.forEach(t=>{const e=document.createElement("style");e.textContent=t.cssText,this.renderRoot.appendChild(e)}))}render(){}}ht.finalized=!0,ht.render=(t,e,o)=>{if(!o||"object"!=typeof o||!o.scopeName)throw new Error("The `scopeName` option is required.");const s=o.scopeName,r=E.has(e),a=L&&11===e.nodeType&&!!e.host,n=a&&!W.has(s),p=n?document.createDocumentFragment():e;if(((t,e,o)=>{let s=E.get(e);void 0===s&&(i(e,e.firstChild),E.set(e,s=new x(Object.assign({templateFactory:N},o))),s.appendInto(e)),s.setValue(t),s.commit()})(t,p,Object.assign({templateFactory:j(s)},o)),n){const t=E.get(p);E.delete(p);const o=t.value instanceof g?t.value.template:void 0;B(s,p,o),i(e,e.firstChild),e.appendChild(p),E.set(e,t)}!r&&a&&window.ShadyCSS.styleElement(e.host)};const dt=(t,e)=>{history.replaceState(null,"",e)};const ut=ct`
    :host {
      @apply --paper-font-body1;
    }

    app-header-layout,
    ha-app-layout {
      background-color: var(--primary-background-color);
    }

    app-header, app-toolbar {
      background-color: var(--primary-color);
      font-weight: 400;
      color: var(--text-primary-color, white);
    }

    app-toolbar ha-menu-button + [main-title],
    app-toolbar ha-paper-icon-button-arrow-prev + [main-title],
    app-toolbar paper-icon-button + [main-title] {
      margin-left: 24px;
    }

    button.link {
      background: none;
      color: inherit;
      border: none;
      padding: 0;
      font: inherit;
      text-align: left;
      text-decoration: underline;
      cursor: pointer;
    }

    .card-actions a {
      text-decoration: none;
    }

    .card-actions .warning {
      --mdc-theme-primary: var(--google-red-500);
    }
`,mt=ct`
    :host {
      font-family: var(--paper-font-body1_-_font-family); -webkit-font-smoothing: var(--paper-font-body1_-_-webkit-font-smoothing); font-size: var(--paper-font-body1_-_font-size); font-weight: var(--paper-font-body1_-_font-weight); line-height: var(--paper-font-body1_-_line-height);
    }

    app-header-layout, ha-app-layout {
      background-color: var(--primary-background-color);
    }

    app-header, app-toolbar, paper-tabs {
      background-color: var(--primary-color);
      font-weight: 400;
      text-transform: uppercase;
      color: var(--text-primary-color, white);
    }

    paper-tabs {
      --paper-tabs-selection-bar-color: #fff;
      margin-left: 12px;
    }

    app-toolbar ha-menu-button + [main-title], app-toolbar ha-paper-icon-button-arrow-prev + [main-title], app-toolbar paper-icon-button + [main-title] {
      margin-left: 24px;
    }
`,yt=ct`
    :host {
        --hacs-status-installed: #126e15;
        --hacs-status-pending-restart: #a70000;
        --hacs-status-pending-update: #ffab40;
        --hacs-status-default: var(--primary-text-color);
        --hacs-badge-color: var(--primary-color);
        --hacs-badge-text-color: var(--primary-text-color);
      }
`,gt=[ut,mt,ct`
    :root {
        font-family: var(--paper-font-body1_-_font-family);
        -webkit-font-smoothing: var(--paper-font-body1_-_-webkit-font-smoothing);
        font-size: var(--paper-font-body1_-_font-size);
        font-weight: var(--paper-font-body1_-_font-weight);
        line-height: var(--paper-font-body1_-_line-height);
    }
    a {
        text-decoration: none;
        color: var(--dark-primary-color);
    }
    h1 {
        font-family: var(--paper-font-title_-_font-family);
        -webkit-font-smoothing: var(--paper-font-title_-_-webkit-font-smoothing);
        white-space: var(--paper-font-title_-_white-space);
        overflow: var(--paper-font-title_-_overflow);
        text-overflow: var(--paper-font-title_-_text-overflow);
        font-size: var(--paper-font-title_-_font-size);
        font-weight: var(--paper-font-title_-_font-weight);
        line-height: var(--paper-font-title_-_line-height);
        @apply --paper-font-title;
    }
    .title {
        margin-bottom: 16px;
        padding-top: 4px;
        color: var(--primary-text-color);
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    .addition {
        color: var(--secondary-text-color);
        position: relative;
        height: auto;
        line-height: 1.2em;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    paper-card {
        cursor: pointer;
    }
    ha-card {
      margin: 8px;
    }
    ha-icon {
        height: 24px;
        width: 24px;
        margin-right: 16px;
        float: left;
        color: var(--primary-text-color);
    }
    ha-icon.installed {
        color: var(--hacs-status-installed);
    }
    ha-icon.pending-upgrade {
        color: var(--hacs-status-pending-update);
    }
    ha-icon.pending-restart {
        color: var(--hacs-status-pending-restart);
    }
`,yt];let vt=class extends ht{constructor(){super(...arguments),this.repository_view=!1,this.SearchTerm=""}render(){if("repository"===this.panel)return U`
      <hacs-panel-repository
        .hass=${this.hass}
        .configuration=${this.configuration}
        .repositories=${this.repositories}
        .repository=${this.repository}
      >
      </hacs-panel-repository>`;{const o=this.panel,s=this.configuration;this.SearchTerm=localStorage.getItem("hacs-search");var t=this.SearchTerm,e=this.repositories.filter((function(e){if("installed"!==o){if("172733314"===e.id)return!1;if(e.hide)return!1;if(null!==s.country&&s.country!==e.country)return!1}else if(e.installed)return!0;return e.category===o&&(""===t||(!!e.name.toLowerCase().includes(t)||(!!e.description.toLowerCase().includes(t)||(!!e.full_name.toLowerCase().includes(t)||(!!String(e.authors).toLowerCase().includes(t)||!!String(e.topics).toLowerCase().includes(t))))))}));return U`
      <paper-input
        class="search-bar search-bar-${this.panel}"
        type="text"
        id="Search"
        @input=${this.DoSearch}
        placeholder="  ${this.hass.localize("component.hacs.store.placeholder_search")}."
        autofocus
        .value=${this.SearchTerm}
      ></paper-input>

    <div class="card-group">
    ${e.sort((t,e)=>t.name>e.name?1:-1).map(t=>U`

      ${"Table"!==this.configuration.frontend_mode?U`
        <paper-card @click="${this.ShowRepository}" .RepoID="${t.id}">
        <div class="card-content">
          <div>
            <ha-icon
              icon="mdi:cube"
              class="${t.status}"
              title="${t.status_description}"
              >
            </ha-icon>
            <div>
              <div class="title">${t.name}</div>
              <div class="addition">${t.description}</div>
            </div>
          </div>
        </div>
        </paper-card>

      `:U`

      <paper-item .RepoID=${t.id} @click="${this.ShowRepository}">
        <div class="icon">
          <ha-icon
            icon="mdi:cube"
            class="${t.status}"
            title="${t.status_description}">
        </ha-icon>
        </div>
        <paper-item-body two-line>
          <div>${t.name}</div>
          <div class="addition">${t.description}</div>
        </paper-item-body>
      </paper-item>
      `}


      `)}
    </div>
    <script>
    var objDiv = document.getElementById("191563578");
    objDiv.scrollTop = objDiv.scrollHeight;
    console.log("done")
    </script>
          `}}DoSearch(t){this.SearchTerm=t.composedPath()[0].value.toLowerCase(),localStorage.setItem("hacs-search",this.SearchTerm)}ShowRepository(t){var e;t.composedPath().forEach(t=>{t.RepoID&&(e=t.RepoID)}),this.panel="repository",this.repository=e,this.repository_view=!0,this.requestUpdate(),dt(0,`/hacs/repository/${e}`)}static get styles(){return[gt,ct`
      paper-item {
        margin-bottom: 24px;
      }
      paper-item:hover {
        outline: 0;
        background: var(--table-row-alternative-background-color);
    }
      .search-bar {
        display: block;
        width: 92%;
        margin-left: 3.4%;
        margin-top: 2%;
        background-color: var(--primary-background-color);
        color: var(--primary-text-color);
        line-height: 32px;
        border-color: var(--dark-primary-color);
        border-width: inherit;
        border-bottom-width: thin;
      }

      .search-bar-installed, .search-bar-settings {
        display: none;
      }

      .card-group {
          margin-top: 24px;
          width: 95%;
          margin-left: 2.5%;
        }

        .card-group .title {
          color: var(--primary-text-color);
          margin-bottom: 12px;
        }

        .card-group .description {
          font-size: 0.5em;
          font-weight: 500;
          margin-top: 4px;
        }

        .card-group paper-card {
          --card-group-columns: 3;
          width: calc((100% - 12px * var(--card-group-columns)) / var(--card-group-columns));
          margin: 4px;
          vertical-align: top;
          height: 136px;
        }

        @media screen and (max-width: 1200px) and (min-width: 601px) {
          .card-group paper-card {
            --card-group-columns: 2;
          }
        }

        @media screen and (max-width: 600px) and (min-width: 0) {
          .card-group paper-card {
            width: 100%;
            margin: 4px 0;
          }
          .content {
            padding: 0;
          }
        }
    `]}};t([rt()],vt.prototype,"hass",void 0),t([rt()],vt.prototype,"repositories",void 0),t([rt()],vt.prototype,"configuration",void 0),t([rt()],vt.prototype,"panel",void 0),t([rt()],vt.prototype,"repository_view",void 0),t([rt()],vt.prototype,"repository",void 0),t([rt()],vt.prototype,"SearchTerm",void 0),vt=t([ot("hacs-panel")],vt);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const ft=new WeakMap,_t=(t=>(...o)=>{const s=t(...o);return e.set(s,!0),s})(t=>e=>{if(!(e instanceof x))throw new Error("unsafeHTML can only be used in text bindings");const o=ft.get(e);if(void 0!==o&&_(t)&&t===o.value&&e.value===o.fragment)return;const s=document.createElement("template");s.innerHTML=t;const i=document.importNode(s.content,!0);e.setValue(i),ft.set(e,{value:t,fragment:i})});let bt=class extends ht{render(){return"0"===String(this.authors.length)?U``:U`
            <div class="autors">
                <p><b>${this.hass.localize("component.hacs.repository.authors")}: </b>

                    ${this.authors.map(t=>U`
                        <a href="https://github.com/${t.replace("@","")}"
                                target="_blank" rel='noreferrer'>
                            ${t.replace("@","")}
                        </a>`)}

                </p>
            </div>
            `}static get styles(){return[gt,ct`
            .autors {

            }
        `]}};t([rt()],bt.prototype,"hass",void 0),t([rt()],bt.prototype,"authors",void 0),bt=t([ot("hacs-authors")],bt);let wt=class extends ht{render(){return U`
            <div class="lovelace-hint">
                <p class="example-title">${this.hass.localize("component.hacs.repository.lovelace_instruction")}:</p>
                <pre id="LovelaceExample" class="yaml">
- url: /community_plugin/${this.repository.full_name.split("/")[1]}/${this.repository.file_name}
  type: ${void 0!==this.repository.javascript_type?U`${this.repository.javascript_type}`:U`${this.hass.localize("component.hacs.repository.lovelace_no_js_type")}`}</pre>

                <paper-icon-button
                    title="${this.hass.localize("component.hacs.repository.lovelace_copy_example")}"
                    icon="mdi:content-copy"
                    @click="${this.CopyToLovelaceExampleToClipboard}"
                    role="button"
                ></paper-icon-button>
            </div>
            `}CopyToLovelaceExampleToClipboard(t){var e=t.composedPath()[4].children[0].children[1].innerText;document.addEventListener("copy",t=>{t.clipboardData.setData("text/plain",e),t.preventDefault(),document.removeEventListener("copy",null)}),document.execCommand("copy")}static get styles(){return[gt,ct`
            .lovelace-hint {

            }
            .example-title {
                margin-block-end: 0em;
            }
            .yaml {
                font-family: monospace, monospace;
                font-size: 1em;
                border-style: solid;
                border-width: thin;
                margin: 0;
                overflow: auto;
                display: inline-flex;
                width: calc(100% - 46px);
                white-space: pre-wrap;
            }

        `]}};t([rt()],wt.prototype,"hass",void 0),t([rt()],wt.prototype,"configuration",void 0),t([rt()],wt.prototype,"repository",void 0),wt=t([ot("hacs-lovelace-hint")],wt);let St=class extends ht{render(){return U`
            <div class="repository-note">
            <p>${this.hass.localize("component.hacs.repository.note_installed")} '${this.repository.local_path}'

            ${"appdaemon"===this.repository.category?U`,
            ${this.hass.localize(`component.hacs.repository.note_${this.repository.category}`)}`:""}

            ${"integration"===this.repository.category?U`,
            ${this.hass.localize(`component.hacs.repository.note_${this.repository.category}`)}`:""}

            ${"plugin"===this.repository.category?U`,
            ${this.hass.localize(`component.hacs.repository.note_${this.repository.category}`)}`:""}

            .</p>

                ${"plugin"===this.repository.category?U`
                    <hacs-lovelace-hint
                        .hass=${this.hass}
                        .configuration=${this.configuration}
                        .repository=${this.repository}
                    ></hacs-lovelace-hint>
                `:""}
            </div>
            `}static get styles(){return[gt,ct`
            .repository-note {
                border-top: 1px solid var(--primary-text-color);
            }
            p {
                font-style: italic;
            }
        `]}};t([rt()],St.prototype,"hass",void 0),t([rt()],St.prototype,"configuration",void 0),t([rt()],St.prototype,"repository",void 0),St=t([ot("hacs-repository-note")],St);let xt=class extends ht{constructor(){super(...arguments),this.repository_view=!1}ResetSpinner(){this.ActiveSpinnerMainAction=!1,this.ActiveSpinnerUninstall=!1,this.ActiveSpinnerLoader=!1}RepositoryWebSocketAction(t,e){let o;"install"===t?this.ActiveSpinnerMainAction=!0:"uninstall"===t?this.ActiveSpinnerUninstall=!0:this.ActiveSpinnerLoader=!0,o=e?{type:"hacs/repository/data",action:t,repository:this.repository,data:e}:{type:"hacs/repository",action:t,repository:this.repository},this.hass.connection.sendMessagePromise(o).then(t=>{this.repositories=t,this.ResetSpinner(),this.requestUpdate()},t=>{console.error("Message failed!",t),this.ResetSpinner(),this.requestUpdate()})}firstUpdated(){this.repo.updated_info||this.RepositoryWebSocketAction("update"),this.ActiveSpinnerMainAction=!1,this.ActiveSpinnerUninstall=!1}render(){if(void 0===this.repository)return U`
      <hacs-panel
        .hass=${this.hass}
        .configuration=${this.configuration}
        .repositories=${this.repositories}
        .panel=${this.panel}
        .repository_view=${this.repository_view}
        .repository=${this.repository}
      >
      </hacs-panel>
      `;var t=this.repository,e=this.repositories.filter((function(e){return e.id===t}));if(this.repo=e[0],this.repo.installed)var o=`\n        ${this.hass.localize("component.hacs.repository.back_to")} ${this.hass.localize("component.hacs.repository.installed")}\n        `;else{if("appdaemon"===this.repo.category)var s="appdaemon_apps";else s=`${this.repo.category}s`;o=`\n        ${this.hass.localize("component.hacs.repository.back_to")} ${this.hass.localize(`component.hacs.common.${s}`)}\n        `}return U`

    <div class="getBack">
      <mwc-button @click=${this.GoBackToStore} title="${o}">
      <ha-icon  icon="mdi:arrow-left"></ha-icon>
        ${o}
      </mwc-button>
      ${this.ActiveSpinnerLoader?U`<paper-spinner active class="loader"></paper-spinner>`:""}
    </div>


    <ha-card header="${this.repo.name}">
      <paper-menu-button no-animations horizontal-align="right" role="group" aria-haspopup="true" vertical-align="top" aria-disabled="false">
        <paper-icon-button icon="hass:dots-vertical" slot="dropdown-trigger" role="button"></paper-icon-button>
        <paper-listbox slot="dropdown-content" role="listbox" tabindex="0">

        <paper-item @click=${this.RepositoryReload}>
        ${this.hass.localize("component.hacs.repository.update_information")}
        </paper-item>

      ${"version"===this.repo.version_or_commit?U`
      <paper-item @click=${this.RepositoryBeta}>
      ${this.repo.beta?this.hass.localize("component.hacs.repository.hide_beta"):this.hass.localize("component.hacs.repository.show_beta")}
        </paper-item>`:""}

        ${this.repo.custom?"":U`
        <paper-item @click=${this.RepositoryHide}>
          ${this.hass.localize("component.hacs.repository.hide")}
        </paper-item>`}

        <a href="https://github.com/${this.repo.full_name}" rel='noreferrer' target="_blank">
          <paper-item>
            <ha-icon class="link-icon" icon="mdi:open-in-new"></ha-icon>
            ${this.hass.localize("component.hacs.repository.open_issue")}
          </paper-item>
        </a>

        <a href="https://github.com" rel='noreferrer' target="_blank">
          <paper-item>
            <ha-icon class="link-icon" icon="mdi:open-in-new"></ha-icon>
            ${this.hass.localize("component.hacs.repository.flag_this")}
          </paper-item>
        </a>

        </paper-listbox>
      </paper-menu-button>
      <div class="card-content">
        <div class="description addition">
          ${this.repo.description}
        </div>
        <div class="information">
          ${this.repo.installed?U`
          <div class="version installed">
            <b>${this.hass.localize("component.hacs.repository.installed")}: </b> ${this.repo.installed_version}
          </div>
          `:""}

        ${"0"===String(this.repo.releases.length)?U`
              <div class="version-available">
                  <b>${this.hass.localize("component.hacs.repository.available")}: </b> ${this.repo.available_version}
              </div>
          `:U`
              <div class="version-available">
                  <paper-dropdown-menu
                    label="${this.hass.localize("component.hacs.repository.available")}:
                     (${this.hass.localize("component.hacs.repository.newest")}: ${this.repo.releases[0]})">
                      <paper-listbox slot="dropdown-content" selected="-1">
                          ${this.repo.releases.map(t=>U`<paper-item @click="${this.SetVersion}">${t}</paper-item>`)}
                          <paper-item @click="${this.SetVersion}">${this.repo.default_branch}</paper-item>
                      </paper-listbox>
                  </paper-dropdown-menu>
              </div>`}

        </div>
        <hacs-authors .hass=${this.hass} .authors=${this.repo.authors}></hacs-authors>
      </div>


      <div class="card-actions">

      <mwc-button @click=${this.RepositoryInstall}>
        ${this.ActiveSpinnerMainAction?U`<paper-spinner active></paper-spinner>`:U`
        ${this.hass.localize(`component.hacs.repository.${this.repo.main_action.toLowerCase()}`)}
        `}
      </mwc-button>

      ${this.repo.pending_upgrade?U`
      <a href="https://github.com/${this.repo.full_name}/releases" rel='noreferrer' target="_blank">
        <mwc-button>
        ${this.hass.localize("component.hacs.repository.changelog")}
        </mwc-button>
      </a>`:""}

        <a href="https://github.com/${this.repo.full_name}" rel='noreferrer' target="_blank">
          <mwc-button>
          ${this.hass.localize("component.hacs.repository.repository")}
          </mwc-button>
        </a>

      ${this.repo.installed?U`
        <mwc-button class="right" @click=${this.RepositoryUnInstall}>
        ${this.ActiveSpinnerUninstall?U`<paper-spinner active></paper-spinner>`:U`
        ${this.hass.localize("component.hacs.repository.uninstall")}
        `}
        </mwc-button>`:""}


      </div>
    </ha-card>

    <ha-card>
      <div class="card-content">
        <div class="more_info">
          ${_t(this.repo.additional_info)}
        </div>
      <hacs-repository-note
        .hass=${this.hass}
        .configuration=${this.configuration}
        .repository=${this.repo}
      ></hacs-repository-note>
      </div>
    </ha-card>
          `}RepositoryReload(){this.RepositoryWebSocketAction("update")}RepositoryInstall(){this.RepositoryWebSocketAction("install")}RepositoryUnInstall(){this.RepositoryWebSocketAction("uninstall")}RepositoryBeta(){this.repo.beta?this.RepositoryWebSocketAction("hide_beta"):this.RepositoryWebSocketAction("show_beta")}RepositoryHide(){this.repo.hide?this.RepositoryWebSocketAction("unhide"):this.RepositoryWebSocketAction("hide")}SetVersion(t){var e=t.composedPath()[2].outerText;e&&this.RepositoryWebSocketAction("set_version",e)}GoBackToStore(){this.repository=void 0,this.repo.installed?this.panel="installed":this.panel=this.repo.category,dt(0,`/hacs/${this.panel}`),this.requestUpdate()}static get styles(){return[gt,ct`
      paper-dropdown-menu {
        width: 250px;
        margin-top: -24px;

      }
      paper-spinner.loader {
        position: absolute;
        top: 20%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 99;
        width: 300px;
        height: 300px;
     }
      .description {
        font-style: italic;
        padding-bottom: 16px;
      }
      .version {
        padding-bottom: 8px;
      }
      .options {
        float: right;
        width: 40%;
      }
      .information {
        width: 60%;
      }
      .getBack {
        margin-top: 8px;
        margin-bottom: 4px;
        margin-left: 5%;
      }
      .right {
        float: right;
      }
      .loading {
        text-align: center;
        width: 100%;
      }
      ha-card {
        width: 90%;
        margin-left: 5%;
      }
      .link-icon {
        color: var(--dark-primary-color);
        margin-right: 8px;
      }
      paper-menu-button {
        float: right;
        top: -65px;
      }
    `]}};t([rt()],xt.prototype,"hass",void 0),t([rt()],xt.prototype,"repositories",void 0),t([rt()],xt.prototype,"configuration",void 0),t([rt()],xt.prototype,"repository",void 0),t([rt()],xt.prototype,"panel",void 0),t([rt()],xt.prototype,"repository_view",void 0),t([rt()],xt.prototype,"ActiveSpinnerMainAction",void 0),t([rt()],xt.prototype,"ActiveSpinnerUninstall",void 0),t([rt()],xt.prototype,"ActiveSpinnerLoader",void 0),xt=t([ot("hacs-panel-repository")],xt);let $t=class extends ht{Delete(t){window.confirm(this.hass.localize("component.hacs.confirm.delete","item",t.composedPath()[3].innerText))&&this.hass.connection.sendMessagePromise({type:"hacs/repository",action:"delete",repository:t.composedPath()[4].repoID}).then(t=>{this.repositories=t,this.requestUpdate()},t=>{console.error("Message failed!",t)})}Save(t){this.SaveSpinner=!0,console.log(t.composedPath()[1].children[0].value),console.log(t.composedPath()[1].children[1].selectedItem.category),this.hass.connection.sendMessagePromise({type:"hacs/repository/data",action:"add",repository:t.composedPath()[1].children[0].value,data:t.composedPath()[1].children[1].selectedItem.category}).then(t=>{this.repositories=t,this.SaveSpinner=!1,this.requestUpdate()},t=>{console.error("Message failed!",t)})}render(){return this.custom=this.repositories.filter((function(t){return!!t.custom})),U`
        <ha-card header="${this.hass.localize("component.hacs.settings.custom_repositories")}">
            <div class="card-content">
            <div class="custom-repositories-list">

            ${this.custom.sort((t,e)=>t.full_name>e.full_name?1:-1).map(t=>U`
                <div class="row" .repoID=${t.id}>
                    <paper-item>
                        ${t.full_name}
                        <ha-icon
                        title="${this.hass.localize("component.hacs.settings.delete")}"
                        class="listicon" icon="mdi:delete"
                        @click=${this.Delete}
                        ></ha-icon>
                    </paper-item>
                </div>
                `)}
            </div>
            </div>

            <div class="card-actions">
                <paper-input class="inputfield" placeholder=${this.hass.localize("component.hacs.settings.add_custom_repository")} type="text"></paper-input>


                <paper-dropdown-menu class="category"
                label="${this.hass.localize("component.hacs.settings.category")}">
                  <paper-listbox slot="dropdown-content" selected="-1">
                      ${this.configuration.categories.map(t=>U`
                      <paper-item .category=${t}>
                        ${this.hass.localize(`component.hacs.common.${t}`)}
                      </paper-item>`)}
                  </paper-listbox>
              </paper-dropdown-menu>

                ${this.SaveSpinner?U`<paper-spinner active class="loading"></paper-spinner>`:U`
                <ha-icon title="${this.hass.localize("component.hacs.settings.save")}"
                    icon="mdi:content-save" class="saveicon"
                    @click=${this.Save}>
                </ha-icon>
                `}
            </div>

        </ha-card>
            `}static get styles(){return[gt,ct`
            ha-card {
                width: 90%;
                margin-left: 5%;
            }
            .custom-repositories {

            }

            .add-repository {

            }
            .inputfield {
                width: 60%;
            }
            .category {
                position: absolute;
                width: 30%;
                right: 54px;
                bottom: 5px;
            }
            .saveicon {
                color: var(--primary-color);
                position: absolute;
                right: 0;
                bottom: 24px;
            }
            .listicon {
                color: var(--primary-color);
                right: 0px;
                position: absolute;
            }
            .loading {
                position: absolute;
                right: 10px;
                bottom: 22px;
            }
        `]}};t([rt()],$t.prototype,"hass",void 0),t([rt()],$t.prototype,"repositories",void 0),t([rt()],$t.prototype,"custom",void 0),t([rt()],$t.prototype,"configuration",void 0),t([rt()],$t.prototype,"SaveSpinner",void 0),$t=t([ot("hacs-custom-repositories")],$t);let Pt=class extends ht{ResetSpinner(){this.ActiveSpinnerReload=!1,this.ActiveSpinnerUpgradeAll=!1}render(){return U`

    <ha-card header="${this.hass.localize("component.hacs.config.title")}">
      <div class="card-content">
        <p><b>${this.hass.localize("component.hacs.common.version")}:</b> ${this.configuration.version}</p>
        <p><b>${this.hass.localize("component.hacs.common.repositories")}:</b> ${this.repositories.length}</p>
        <div class="version-available">
        <paper-dropdown-menu label="${this.hass.localize("component.hacs.settings.display")}">
            <paper-listbox slot="dropdown-content" selected="-1">
              <paper-item .display="grid" @click="${this.SetFeStyleGrid}">
                ${this.hass.localize("component.hacs.settings.grid")}
              </paper-item>
              <paper-item .display="table" @click="${this.SetFeStyleTable}">
                ${this.hass.localize("component.hacs.settings.table")}
              </paper-item>
            </paper-listbox>
        </paper-dropdown-menu>
    </div>
      </div>
      <div class="card-actions">

      <mwc-button raised @click=${this.ReloadData}>
        ${this.ActiveSpinnerReload?U`<paper-spinner active></paper-spinner>`:U`
        ${this.hass.localize("component.hacs.settings.reload_data")}
        `}
      </mwc-button>

      <mwc-button raised @click=${this.UpgradeAll}>
        ${this.ActiveSpinnerUpgradeAll?U`<paper-spinner active></paper-spinner>`:U`
        ${this.hass.localize("component.hacs.settings.upgrade_all")}
        `}
      </mwc-button>

      <a href="https://github.com/custom-components/hacs" target="_blank" rel="noreferrer">
        <mwc-button raised>
          ${this.hass.localize("component.hacs.settings.hacs_repo")}
        </mwc-button>
      </a>

      <a href="https://github.com/custom-components/hacs/issues" target="_blank" rel="noreferrer">
        <mwc-button raised>
          ${this.hass.localize("component.hacs.repository.open_issue")}
        </mwc-button>
      </a>
      </div>
    </ha-card>
    <hacs-custom-repositories
      .hass=${this.hass}
      .configuration=${this.configuration}
      .repositories=${this.repositories}
    >
    </hacs-custom-repositories>
          `}SetFeStyleGrid(){this.hass.connection.sendMessage({type:"hacs/settings",action:"set_fe_grid"})}SetFeStyleTable(){this.hass.connection.sendMessage({type:"hacs/settings",action:"set_fe_table"})}ReloadData(){this.ActiveSpinnerReload=!0,console.log("This should reload data, but that is not added.")}UpgradeAll(){this.ActiveSpinnerReload=!0,console.log("This should reload data, but that is not added.")}static get styles(){return[gt,ct`
    ha-card {
      width: 90%;
      margin-left: 5%;
    }
    mwc-button {
      margin: 0 8px 0 8px;
    }
    `]}};t([rt()],Pt.prototype,"hass",void 0),t([rt()],Pt.prototype,"repositories",void 0),t([rt()],Pt.prototype,"configuration",void 0),t([rt()],Pt.prototype,"ActiveSpinnerReload",void 0),t([rt()],Pt.prototype,"ActiveSpinnerUpgradeAll",void 0),Pt=t([ot("hacs-panel-settings")],Pt);let kt=class extends ht{constructor(){super(...arguments),this.repository_view=!1}getRepositories(){this.hass.connection.sendMessagePromise({type:"hacs/config"}).then(t=>{this.configuration=t,this.requestUpdate()},t=>{console.error("[hacs/config] Message failed!",t)}),this.hass.connection.sendMessagePromise({type:"hacs/repositories"}).then(t=>{this.repositories=t,this.requestUpdate()},t=>{console.error("[hacs/repositories] Message failed!",t)})}firstUpdated(){localStorage.setItem("hacs-search",""),this.panel=this._page,this.getRepositories(),/repository\//i.test(this.panel)?(this.repository_view=!0,this.repository=this.panel.split("/")[1]):this.repository_view=!1,function(){if(customElements.get("hui-view"))return!0;const t=document.createElement("partial-panel-resolver");t.hass=document.querySelector("home-assistant").hass,t.route={path:"/lovelace/"};try{document.querySelector("home-assistant").appendChild(t).catch(t=>{})}catch(e){document.querySelector("home-assistant").removeChild(t)}customElements.get("hui-view")}(),this.hass.connection.sendMessagePromise({type:"hacs/repository"}),this.hass.connection.sendMessagePromise({type:"hacs/config"}),this.hass.connection.subscribeEvents(()=>this.getRepositories(),"hacs/repository"),this.hass.connection.subscribeEvents(()=>this.getRepositories(),"hacs/config")}render(){if(""===this.panel&&(dt(0,"/hacs/installed"),this.panel="installed"),void 0===this.repositories)return U`<paper-spinner active class="loader"></paper-spinner>`;/repository\//i.test(this.panel)?(this.repository_view=!0,this.repository=this.panel.split("/")[1],this.panel=this.panel.split("/")[0]):this.repository_view=!1;const t=this.panel;return U`
    <app-header-layout has-scrolling-region>
    <app-header slot="header" fixed>
        <app-toolbar>
        <ha-menu-button .hass="${this.hass}" .narrow="${this.narrow}"></ha-menu-button>
        <div main-title>${this.hass.localize("component.hacs.config.title")}</div>
        </app-toolbar>
    <paper-tabs
    scrollable
    attr-for-selected="page-name"
    .selected=${t}
    @iron-activate=${this.handlePageSelected}>

    <paper-tab page-name="installed">
    ${this.hass.localize("component.hacs.common.installed")}
    </paper-tab>

    <paper-tab page-name="integration">
    ${this.hass.localize("component.hacs.common.integrations")}
    </paper-tab>

    <paper-tab page-name="plugin">
    ${this.hass.localize("component.hacs.common.plugins")}
    </paper-tab>

    ${this.configuration.appdaemon?U`<paper-tab page-name="appdaemon">
        ${this.hass.localize("component.hacs.common.appdaemon_apps")}
    </paper-tab>`:""}

    ${this.configuration.python_script?U`<paper-tab page-name="python_script">
        ${this.hass.localize("component.hacs.common.python_scripts")}
    </paper-tab>`:""}

    ${this.configuration.theme?U`<paper-tab page-name="theme">
        ${this.hass.localize("component.hacs.common.themes")}
    </paper-tab>`:""}

    <paper-tab page-name="settings">
    ${this.hass.localize("component.hacs.common.settings")}
    </paper-tab>
    </paper-tabs>
    </app-header>

    ${this.panel,U`
    <hacs-panel
    .hass=${this.hass}
    .configuration=${this.configuration}
    .repositories=${this.repositories}
    .panel=${this.panel}
    .repository_view=${this.repository_view}
    .repository=${this.repository}
    >
    </hacs-panel>`}

    ${"settings"===this.panel?U`
    <hacs-panel-settings
        .hass=${this.hass}
        .configuration=${this.configuration}
        .repositories=${this.repositories}>
        </hacs-panel-settings>`:""}

    </app-header-layout>`}handlePageSelected(t){this.repository_view=!1;const e=t.detail.item.getAttribute("page-name");this.panel=e,this.requestUpdate(),e!==this._page&&dt(0,`/hacs/${e}`),function(t,e){const o=e,s=Math.random(),i=Date.now(),r=o.scrollTop,a=0-r;t._currentAnimationId=s,function e(){const n=Date.now()-i;var p;n>200?o.scrollTop=0:t._currentAnimationId===s&&(o.scrollTop=(p=n,-a*(p/=200)*(p-2)+r),requestAnimationFrame(e.bind(t)))}.call(t)}(this,this.shadowRoot.querySelector("app-header-layout").header.scrollTarget)}get _page(){return null===this.route.path.substr(1)?"installed":this.route.path.substr(1)}static get styles(){return[gt,ct`
    paper-spinner.loader {
      position: absolute;
      top: 20%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 99;
      width: 300px;
      height: 300px;
   }
    `]}};t([rt()],kt.prototype,"hass",void 0),t([rt()],kt.prototype,"repositories",void 0),t([rt()],kt.prototype,"configuration",void 0),t([rt()],kt.prototype,"route",void 0),t([rt()],kt.prototype,"narrow",void 0),t([rt()],kt.prototype,"panel",void 0),t([rt()],kt.prototype,"repository",void 0),t([rt()],kt.prototype,"repository_view",void 0),kt=t([ot("hacs-frontend")],kt);
