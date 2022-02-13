/*! *****************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */
/* global Reflect, Promise */

var extendStatics = function(d, b) {
    extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
    return extendStatics(d, b);
};

function __extends(d, b) {
    if (typeof b !== "function" && b !== null)
        throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
}

var __assign = function() {
    __assign = Object.assign || function __assign(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};

function __rest(s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
}

function __decorate(decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
}

function __param(paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
}

function __metadata(metadataKey, metadataValue) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(metadataKey, metadataValue);
}

function __awaiter(thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
}

function __generator(thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
}

var __createBinding = Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
});

function __exportStar(m, o) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(o, p)) __createBinding(o, m, p);
}

function __values(o) {
    var s = typeof Symbol === "function" && Symbol.iterator, m = s && o[s], i = 0;
    if (m) return m.call(o);
    if (o && typeof o.length === "number") return {
        next: function () {
            if (o && i >= o.length) o = void 0;
            return { value: o && o[i++], done: !o };
        }
    };
    throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
}

function __read(o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
}

/** @deprecated */
function __spread() {
    for (var ar = [], i = 0; i < arguments.length; i++)
        ar = ar.concat(__read(arguments[i]));
    return ar;
}

/** @deprecated */
function __spreadArrays() {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
}

function __spreadArray(to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
}

function __await(v) {
    return this instanceof __await ? (this.v = v, this) : new __await(v);
}

function __asyncGenerator(thisArg, _arguments, generator) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var g = generator.apply(thisArg, _arguments || []), i, q = [];
    return i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i;
    function verb(n) { if (g[n]) i[n] = function (v) { return new Promise(function (a, b) { q.push([n, v, a, b]) > 1 || resume(n, v); }); }; }
    function resume(n, v) { try { step(g[n](v)); } catch (e) { settle(q[0][3], e); } }
    function step(r) { r.value instanceof __await ? Promise.resolve(r.value.v).then(fulfill, reject) : settle(q[0][2], r); }
    function fulfill(value) { resume("next", value); }
    function reject(value) { resume("throw", value); }
    function settle(f, v) { if (f(v), q.shift(), q.length) resume(q[0][0], q[0][1]); }
}

function __asyncDelegator(o) {
    var i, p;
    return i = {}, verb("next"), verb("throw", function (e) { throw e; }), verb("return"), i[Symbol.iterator] = function () { return this; }, i;
    function verb(n, f) { i[n] = o[n] ? function (v) { return (p = !p) ? { value: __await(o[n](v)), done: n === "return" } : f ? f(v) : v; } : f; }
}

function __asyncValues(o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
}

function __makeTemplateObject(cooked, raw) {
    if (Object.defineProperty) { Object.defineProperty(cooked, "raw", { value: raw }); } else { cooked.raw = raw; }
    return cooked;
};

var __setModuleDefault = Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
};

function __importStar(mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
}

function __importDefault(mod) {
    return (mod && mod.__esModule) ? mod : { default: mod };
}

function __classPrivateFieldGet(receiver, state, kind, f) {
    if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
    if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
    return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
}

function __classPrivateFieldSet(receiver, state, value, kind, f) {
    if (kind === "m") throw new TypeError("Private method is not writable");
    if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
    if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
    return (kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value)), value;
}

/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t$4=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e$7=Symbol(),n$5=new Map;class s$4{constructor(t,n){if(this._$cssResult$=!0,n!==e$7)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t;}get styleSheet(){let e=n$5.get(this.cssText);return t$4&&void 0===e&&(n$5.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const o$6=t=>new s$4("string"==typeof t?t:t+"",e$7),r$4=(t,...n)=>{const o=1===t.length?t[0]:n.reduce(((e,n,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+t[s+1]),t[0]);return new s$4(o,e$7)},i$4=(e,n)=>{t$4?e.adoptedStyleSheets=n.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):n.forEach((t=>{const n=document.createElement("style"),s=window.litNonce;void 0!==s&&n.setAttribute("nonce",s),n.textContent=t.cssText,e.appendChild(n);}));},S$2=t$4?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const n of t.cssRules)e+=n.cssText;return o$6(e)})(t):t;

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var s$3,e$6;const r$3={toAttribute(t,i){switch(i){case Boolean:t=t?"":null;break;case Object:case Array:t=null==t?t:JSON.stringify(t);}return t},fromAttribute(t,i){let s=t;switch(i){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t);}catch(t){s=null;}}return s}},h$3=(t,i)=>i!==t&&(i==i||t==t),o$5={attribute:!0,type:String,converter:r$3,reflect:!1,hasChanged:h$3};class n$4 extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o();}static addInitializer(t){var i;null!==(i=this.l)&&void 0!==i||(this.l=[]),this.l.push(t);}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((i,s)=>{const e=this._$Eh(s,i);void 0!==e&&(this._$Eu.set(e,s),t.push(e));})),t}static createProperty(t,i=o$5){if(i.state&&(i.attribute=!1),this.finalize(),this.elementProperties.set(t,i),!i.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,e=this.getPropertyDescriptor(t,s,i);void 0!==e&&Object.defineProperty(this.prototype,t,e);}}static getPropertyDescriptor(t,i,s){return {get(){return this[i]},set(e){const r=this[t];this[i]=e,this.requestUpdate(t,r,s);},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||o$5}static finalize(){if(this.hasOwnProperty("finalized"))return !1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,i=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of i)this.createProperty(s,t[s]);}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(i){const s=[];if(Array.isArray(i)){const e=new Set(i.flat(1/0).reverse());for(const i of e)s.unshift(S$2(i));}else void 0!==i&&s.push(S$2(i));return s}static _$Eh(t,i){const s=i.attribute;return !1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ev=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Ep(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)));}addController(t){var i,s;(null!==(i=this._$Em)&&void 0!==i?i:this._$Em=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t));}removeController(t){var i;null===(i=this._$Em)||void 0===i||i.splice(this._$Em.indexOf(t)>>>0,1);}_$Ep(){this.constructor.elementProperties.forEach(((t,i)=>{this.hasOwnProperty(i)&&(this._$Et.set(i,this[i]),delete this[i]);}));}createRenderRoot(){var t;const s=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return i$4(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Em)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostConnected)||void 0===i?void 0:i.call(t)}));}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Em)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostDisconnected)||void 0===i?void 0:i.call(t)}));}attributeChangedCallback(t,i,s){this._$AK(t,s);}_$Eg(t,i,s=o$5){var e,h;const n=this.constructor._$Eh(t,s);if(void 0!==n&&!0===s.reflect){const o=(null!==(h=null===(e=s.converter)||void 0===e?void 0:e.toAttribute)&&void 0!==h?h:r$3.toAttribute)(i,s.type);this._$Ei=t,null==o?this.removeAttribute(n):this.setAttribute(n,o),this._$Ei=null;}}_$AK(t,i){var s,e,h;const o=this.constructor,n=o._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=o.getPropertyOptions(n),l=t.converter,a=null!==(h=null!==(e=null===(s=l)||void 0===s?void 0:s.fromAttribute)&&void 0!==e?e:"function"==typeof l?l:null)&&void 0!==h?h:r$3.fromAttribute;this._$Ei=n,this[n]=a(i,t.type),this._$Ei=null;}}requestUpdate(t,i,s){let e=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||h$3)(this[t],i)?(this._$AL.has(t)||this._$AL.set(t,i),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$ES&&(this._$ES=new Map),this._$ES.set(t,s))):e=!1),!this.isUpdatePending&&e&&(this._$Ev=this._$EC());}async _$EC(){this.isUpdatePending=!0;try{await this._$Ev;}catch(t){Promise.reject(t);}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,i)=>this[i]=t)),this._$Et=void 0);let i=!1;const s=this._$AL;try{i=this.shouldUpdate(s),i?(this.willUpdate(s),null===(t=this._$Em)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostUpdate)||void 0===i?void 0:i.call(t)})),this.update(s)):this._$ET();}catch(t){throw i=!1,this._$ET(),t}i&&this._$AE(s);}willUpdate(t){}_$AE(t){var i;null===(i=this._$Em)||void 0===i||i.forEach((t=>{var i;return null===(i=t.hostUpdated)||void 0===i?void 0:i.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t);}_$ET(){this._$AL=new Map,this.isUpdatePending=!1;}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ev}shouldUpdate(t){return !0}update(t){void 0!==this._$ES&&(this._$ES.forEach(((t,i)=>this._$Eg(i,this[i],t))),this._$ES=void 0),this._$ET();}updated(t){}firstUpdated(t){}}n$4.finalized=!0,n$4.elementProperties=new Map,n$4.elementStyles=[],n$4.shadowRootOptions={mode:"open"},null===(s$3=globalThis.reactiveElementPolyfillSupport)||void 0===s$3||s$3.call(globalThis,{ReactiveElement:n$4}),(null!==(e$6=globalThis.reactiveElementVersions)&&void 0!==e$6?e$6:globalThis.reactiveElementVersions=[]).push("1.0.0");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t$3,i$3;const s$2=globalThis.trustedTypes,e$5=s$2?s$2.createPolicy("lit-html",{createHTML:t=>t}):void 0,o$4=`lit$${(Math.random()+"").slice(9)}$`,n$3="?"+o$4,l$2=`<${n$3}>`,h$2=document,r$2=(t="")=>h$2.createComment(t),d$1=t=>null===t||"object"!=typeof t&&"function"!=typeof t,u$1=Array.isArray,v$1=t=>{var i;return u$1(t)||"function"==typeof(null===(i=t)||void 0===i?void 0:i[Symbol.iterator])},c$1=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,a$1=/-->/g,f$1=/>/g,_$1=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,g$1=/'/g,m$1=/"/g,$$1=/^(?:script|style|textarea)$/i,p$1=t=>(i,...s)=>({_$litType$:t,strings:i,values:s}),y$1=p$1(1),b$1=p$1(2),T$1=Symbol.for("lit-noChange"),x$1=Symbol.for("lit-nothing"),w$1=new WeakMap,A$1=(t,i,s)=>{var e,o;const n=null!==(e=null==s?void 0:s.renderBefore)&&void 0!==e?e:i;let l=n._$litPart$;if(void 0===l){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;n._$litPart$=l=new S$1(i.insertBefore(r$2(),t),t,void 0,null!=s?s:{});}return l._$AI(t),l},C$1=h$2.createTreeWalker(h$2,129,null,!1),P$1=(t,i)=>{const s=t.length-1,n=[];let h,r=2===i?"<svg>":"",d=c$1;for(let i=0;i<s;i++){const s=t[i];let e,u,v=-1,p=0;for(;p<s.length&&(d.lastIndex=p,u=d.exec(s),null!==u);)p=d.lastIndex,d===c$1?"!--"===u[1]?d=a$1:void 0!==u[1]?d=f$1:void 0!==u[2]?($$1.test(u[2])&&(h=RegExp("</"+u[2],"g")),d=_$1):void 0!==u[3]&&(d=_$1):d===_$1?">"===u[0]?(d=null!=h?h:c$1,v=-1):void 0===u[1]?v=-2:(v=d.lastIndex-u[2].length,e=u[1],d=void 0===u[3]?_$1:'"'===u[3]?m$1:g$1):d===m$1||d===g$1?d=_$1:d===a$1||d===f$1?d=c$1:(d=_$1,h=void 0);const y=d===_$1&&t[i+1].startsWith("/>")?" ":"";r+=d===c$1?s+l$2:v>=0?(n.push(e),s.slice(0,v)+"$lit$"+s.slice(v)+o$4+y):s+o$4+(-2===v?(n.push(void 0),i):y);}const u=r+(t[s]||"<?>")+(2===i?"</svg>":"");return [void 0!==e$5?e$5.createHTML(u):u,n]};class V$1{constructor({strings:t,_$litType$:i},e){let l;this.parts=[];let h=0,d=0;const u=t.length-1,v=this.parts,[c,a]=P$1(t,i);if(this.el=V$1.createElement(c,e),C$1.currentNode=this.el.content,2===i){const t=this.el.content,i=t.firstChild;i.remove(),t.append(...i.childNodes);}for(;null!==(l=C$1.nextNode())&&v.length<u;){if(1===l.nodeType){if(l.hasAttributes()){const t=[];for(const i of l.getAttributeNames())if(i.endsWith("$lit$")||i.startsWith(o$4)){const s=a[d++];if(t.push(i),void 0!==s){const t=l.getAttribute(s.toLowerCase()+"$lit$").split(o$4),i=/([.?@])?(.*)/.exec(s);v.push({type:1,index:h,name:i[2],strings:t,ctor:"."===i[1]?k$1:"?"===i[1]?H$1:"@"===i[1]?I$1:M$1});}else v.push({type:6,index:h});}for(const i of t)l.removeAttribute(i);}if($$1.test(l.tagName)){const t=l.textContent.split(o$4),i=t.length-1;if(i>0){l.textContent=s$2?s$2.emptyScript:"";for(let s=0;s<i;s++)l.append(t[s],r$2()),C$1.nextNode(),v.push({type:2,index:++h});l.append(t[i],r$2());}}}else if(8===l.nodeType)if(l.data===n$3)v.push({type:2,index:h});else {let t=-1;for(;-1!==(t=l.data.indexOf(o$4,t+1));)v.push({type:7,index:h}),t+=o$4.length-1;}h++;}}static createElement(t,i){const s=h$2.createElement("template");return s.innerHTML=t,s}}function E$1(t,i,s=t,e){var o,n,l,h;if(i===T$1)return i;let r=void 0!==e?null===(o=s._$Cl)||void 0===o?void 0:o[e]:s._$Cu;const u=d$1(i)?void 0:i._$litDirective$;return (null==r?void 0:r.constructor)!==u&&(null===(n=null==r?void 0:r._$AO)||void 0===n||n.call(r,!1),void 0===u?r=void 0:(r=new u(t),r._$AT(t,s,e)),void 0!==e?(null!==(l=(h=s)._$Cl)&&void 0!==l?l:h._$Cl=[])[e]=r:s._$Cu=r),void 0!==r&&(i=E$1(t,r._$AS(t,i.values),r,e)),i}class N$1{constructor(t,i){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=i;}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var i;const{el:{content:s},parts:e}=this._$AD,o=(null!==(i=null==t?void 0:t.creationScope)&&void 0!==i?i:h$2).importNode(s,!0);C$1.currentNode=o;let n=C$1.nextNode(),l=0,r=0,d=e[0];for(;void 0!==d;){if(l===d.index){let i;2===d.type?i=new S$1(n,n.nextSibling,this,t):1===d.type?i=new d.ctor(n,d.name,d.strings,this,t):6===d.type&&(i=new L$1(n,this,t)),this.v.push(i),d=e[++r];}l!==(null==d?void 0:d.index)&&(n=C$1.nextNode(),l++);}return o}m(t){let i=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,i),i+=s.strings.length-2):s._$AI(t[i])),i++;}}class S$1{constructor(t,i,s,e){var o;this.type=2,this._$AH=x$1,this._$AN=void 0,this._$AA=t,this._$AB=i,this._$AM=s,this.options=e,this._$Cg=null===(o=null==e?void 0:e.isConnected)||void 0===o||o;}get _$AU(){var t,i;return null!==(i=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==i?i:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const i=this._$AM;return void 0!==i&&11===t.nodeType&&(t=i.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,i=this){t=E$1(this,t,i),d$1(t)?t===x$1||null==t||""===t?(this._$AH!==x$1&&this._$AR(),this._$AH=x$1):t!==this._$AH&&t!==T$1&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.S(t):v$1(t)?this.M(t):this.$(t);}A(t,i=this._$AB){return this._$AA.parentNode.insertBefore(t,i)}S(t){this._$AH!==t&&(this._$AR(),this._$AH=this.A(t));}$(t){this._$AH!==x$1&&d$1(this._$AH)?this._$AA.nextSibling.data=t:this.S(h$2.createTextNode(t)),this._$AH=t;}T(t){var i;const{values:s,_$litType$:e}=t,o="number"==typeof e?this._$AC(t):(void 0===e.el&&(e.el=V$1.createElement(e.h,this.options)),e);if((null===(i=this._$AH)||void 0===i?void 0:i._$AD)===o)this._$AH.m(s);else {const t=new N$1(o,this),i=t.p(this.options);t.m(s),this.S(i),this._$AH=t;}}_$AC(t){let i=w$1.get(t.strings);return void 0===i&&w$1.set(t.strings,i=new V$1(t)),i}M(t){u$1(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,e=0;for(const o of t)e===i.length?i.push(s=new S$1(this.A(r$2()),this.A(r$2()),this,this.options)):s=i[e],s._$AI(o),e++;e<i.length&&(this._$AR(s&&s._$AB.nextSibling,e),i.length=e);}_$AR(t=this._$AA.nextSibling,i){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,i);t&&t!==this._$AB;){const i=t.nextSibling;t.remove(),t=i;}}setConnected(t){var i;void 0===this._$AM&&(this._$Cg=t,null===(i=this._$AP)||void 0===i||i.call(this,t));}}class M$1{constructor(t,i,s,e,o){this.type=1,this._$AH=x$1,this._$AN=void 0,this.element=t,this.name=i,this._$AM=e,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=x$1;}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,i=this,s,e){const o=this.strings;let n=!1;if(void 0===o)t=E$1(this,t,i,0),n=!d$1(t)||t!==this._$AH&&t!==T$1,n&&(this._$AH=t);else {const e=t;let l,h;for(t=o[0],l=0;l<o.length-1;l++)h=E$1(this,e[s+l],i,l),h===T$1&&(h=this._$AH[l]),n||(n=!d$1(h)||h!==this._$AH[l]),h===x$1?t=x$1:t!==x$1&&(t+=(null!=h?h:"")+o[l+1]),this._$AH[l]=h;}n&&!e&&this.k(t);}k(t){t===x$1?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"");}}class k$1 extends M$1{constructor(){super(...arguments),this.type=3;}k(t){this.element[this.name]=t===x$1?void 0:t;}}class H$1 extends M$1{constructor(){super(...arguments),this.type=4;}k(t){t&&t!==x$1?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name);}}class I$1 extends M$1{constructor(t,i,s,e,o){super(t,i,s,e,o),this.type=5;}_$AI(t,i=this){var s;if((t=null!==(s=E$1(this,t,i,0))&&void 0!==s?s:x$1)===T$1)return;const e=this._$AH,o=t===x$1&&e!==x$1||t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive,n=t!==x$1&&(e===x$1||o);o&&this.element.removeEventListener(this.name,this,e),n&&this.element.addEventListener(this.name,this,t),this._$AH=t;}handleEvent(t){var i,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(i=this.options)||void 0===i?void 0:i.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t);}}class L$1{constructor(t,i,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=i,this.options=s;}get _$AU(){return this._$AM._$AU}_$AI(t){E$1(this,t);}}const R$1={P:"$lit$",V:o$4,L:n$3,I:1,N:P$1,R:N$1,D:v$1,j:E$1,H:S$1,O:M$1,F:H$1,B:I$1,W:k$1,Z:L$1};null===(t$3=globalThis.litHtmlPolyfillSupport)||void 0===t$3||t$3.call(globalThis,V$1,S$1),(null!==(i$3=globalThis.litHtmlVersions)&&void 0!==i$3?i$3:globalThis.litHtmlVersions=[]).push("2.0.0");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var l$1,o$3,r$1;const s$1=n$4;class n$2 extends n$4{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0;}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const i=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=A$1(i,this.renderRoot,this.renderOptions);}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0);}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1);}render(){return T$1}}n$2.finalized=!0,n$2._$litElement$=!0,null===(l$1=globalThis.litElementHydrateSupport)||void 0===l$1||l$1.call(globalThis,{LitElement:n$2}),null===(o$3=globalThis.litElementPolyfillSupport)||void 0===o$3||o$3.call(globalThis,{LitElement:n$2});const h$1={_$AK:(t,e,i)=>{t._$AK(e,i);},_$AL:t=>t._$AL};(null!==(r$1=globalThis.litElementVersions)&&void 0!==r$1?r$1:globalThis.litElementVersions=[]).push("3.0.0");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e$4=(e,t,o)=>{Object.defineProperty(t,o,e);},t$2=(e,t)=>({kind:"method",placement:"prototype",key:t.key,descriptor:e}),o$2=({finisher:e,descriptor:t})=>(o,n)=>{var r;if(void 0===n){const n=null!==(r=o.originalKey)&&void 0!==r?r:o.key,i=null!=t?{kind:"method",placement:"prototype",key:n,descriptor:t(o.key)}:{...o,key:n};return null!=e&&(i.finisher=function(t){e(t,n);}),i}{const r=o.constructor;void 0!==t&&Object.defineProperty(o,n,t(n)),null==e||e(r,n);}};

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const n$1=n=>e=>"function"==typeof e?((n,e)=>(window.customElements.define(n,e),e))(n,e):((n,e)=>{const{kind:t,elements:i}=e;return {kind:t,elements:i,finisher(e){window.customElements.define(n,e);}}})(n,e);

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const i$2=(i,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(n){n.createProperty(e.key,i);}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this));},finisher(n){n.createProperty(e.key,i);}};function e$3(e){return (n,t)=>void 0!==t?((i,e,n)=>{e.constructor.createProperty(n,i);})(e,n,t):i$2(e,n)}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function t$1(t){return e$3({...t,state:!0})}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function e$2(e){return o$2({finisher:(r,t)=>{Object.assign(r.prototype[t],e);}})}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function i$1(i,n){return o$2({descriptor:o=>{const t={get(){var o,n;return null!==(n=null===(o=this.renderRoot)||void 0===o?void 0:o.querySelector(i))&&void 0!==n?n:null},enumerable:!0,configurable:!0};if(n){const n="symbol"==typeof o?Symbol():"__"+o;t.get=function(){var o,t;return void 0===this[n]&&(this[n]=null!==(t=null===(o=this.renderRoot)||void 0===o?void 0:o.querySelector(i))&&void 0!==t?t:null),this[n]};}return t}})}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function e$1(e){return o$2({descriptor:r=>({get(){var r,o;return null!==(o=null===(r=this.renderRoot)||void 0===r?void 0:r.querySelectorAll(e))&&void 0!==o?o:[]},enumerable:!0,configurable:!0})})}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function e(e){return o$2({descriptor:r=>({async get(){var r;return await this.updateComplete,null===(r=this.renderRoot)||void 0===r?void 0:r.querySelector(e)},enumerable:!0,configurable:!0})})}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function o$1(o="",n=!1,t=""){return o$2({descriptor:e=>({get(){var e,r,l;const i="slot"+(o?`[name=${o}]`:":not([name])");let u=null!==(l=null===(r=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(i))||void 0===r?void 0:r.assignedNodes({flatten:n}))&&void 0!==l?l:[];return t&&(u=u.filter((e=>e.nodeType===Node.ELEMENT_NODE&&e.matches(t)))),u},enumerable:!0,configurable:!0})})}

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */console.warn("The main 'lit-element' module entrypoint is deprecated. Please update your imports to use the 'lit' package: 'lit' and 'lit/decorators.ts' or import from 'lit-element/lit-element.ts'. See https://lit.dev/msg/deprecated-import-path for more information.");

function deepcopy(value) {
  if (!(!!value && typeof value == 'object')) {
    return value;
  }
  if (Object.prototype.toString.call(value) == '[object Date]') {
    return new Date(value.getTime());
  }
  if (Array.isArray(value)) {
    return value.map(deepcopy);
  }
  var result = {};
  Object.keys(value).forEach(
    function(key) { result[key] = deepcopy(value[key]); });
  return result;
}

var token = /d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g;
var twoDigitsOptional = "[1-9]\\d?";
var twoDigits = "\\d\\d";
var threeDigits = "\\d{3}";
var fourDigits = "\\d{4}";
var word = "[^\\s]+";
var literal = /\[([^]*?)\]/gm;
function shorten(arr, sLen) {
    var newArr = [];
    for (var i = 0, len = arr.length; i < len; i++) {
        newArr.push(arr[i].substr(0, sLen));
    }
    return newArr;
}
var monthUpdate = function (arrName) { return function (v, i18n) {
    var lowerCaseArr = i18n[arrName].map(function (v) { return v.toLowerCase(); });
    var index = lowerCaseArr.indexOf(v.toLowerCase());
    if (index > -1) {
        return index;
    }
    return null;
}; };
function assign(origObj) {
    var args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        args[_i - 1] = arguments[_i];
    }
    for (var _a = 0, args_1 = args; _a < args_1.length; _a++) {
        var obj = args_1[_a];
        for (var key in obj) {
            // @ts-ignore ex
            origObj[key] = obj[key];
        }
    }
    return origObj;
}
var dayNames = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
];
var monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
];
var monthNamesShort = shorten(monthNames, 3);
var dayNamesShort = shorten(dayNames, 3);
var defaultI18n = {
    dayNamesShort: dayNamesShort,
    dayNames: dayNames,
    monthNamesShort: monthNamesShort,
    monthNames: monthNames,
    amPm: ["am", "pm"],
    DoFn: function (dayOfMonth) {
        return (dayOfMonth +
            ["th", "st", "nd", "rd"][dayOfMonth % 10 > 3
                ? 0
                : ((dayOfMonth - (dayOfMonth % 10) !== 10 ? 1 : 0) * dayOfMonth) % 10]);
    }
};
var globalI18n = assign({}, defaultI18n);
var setGlobalDateI18n = function (i18n) {
    return (globalI18n = assign(globalI18n, i18n));
};
var regexEscape = function (str) {
    return str.replace(/[|\\{()[^$+*?.-]/g, "\\$&");
};
var pad = function (val, len) {
    if (len === void 0) { len = 2; }
    val = String(val);
    while (val.length < len) {
        val = "0" + val;
    }
    return val;
};
var formatFlags = {
    D: function (dateObj) { return String(dateObj.getDate()); },
    DD: function (dateObj) { return pad(dateObj.getDate()); },
    Do: function (dateObj, i18n) {
        return i18n.DoFn(dateObj.getDate());
    },
    d: function (dateObj) { return String(dateObj.getDay()); },
    dd: function (dateObj) { return pad(dateObj.getDay()); },
    ddd: function (dateObj, i18n) {
        return i18n.dayNamesShort[dateObj.getDay()];
    },
    dddd: function (dateObj, i18n) {
        return i18n.dayNames[dateObj.getDay()];
    },
    M: function (dateObj) { return String(dateObj.getMonth() + 1); },
    MM: function (dateObj) { return pad(dateObj.getMonth() + 1); },
    MMM: function (dateObj, i18n) {
        return i18n.monthNamesShort[dateObj.getMonth()];
    },
    MMMM: function (dateObj, i18n) {
        return i18n.monthNames[dateObj.getMonth()];
    },
    YY: function (dateObj) {
        return pad(String(dateObj.getFullYear()), 4).substr(2);
    },
    YYYY: function (dateObj) { return pad(dateObj.getFullYear(), 4); },
    h: function (dateObj) { return String(dateObj.getHours() % 12 || 12); },
    hh: function (dateObj) { return pad(dateObj.getHours() % 12 || 12); },
    H: function (dateObj) { return String(dateObj.getHours()); },
    HH: function (dateObj) { return pad(dateObj.getHours()); },
    m: function (dateObj) { return String(dateObj.getMinutes()); },
    mm: function (dateObj) { return pad(dateObj.getMinutes()); },
    s: function (dateObj) { return String(dateObj.getSeconds()); },
    ss: function (dateObj) { return pad(dateObj.getSeconds()); },
    S: function (dateObj) {
        return String(Math.round(dateObj.getMilliseconds() / 100));
    },
    SS: function (dateObj) {
        return pad(Math.round(dateObj.getMilliseconds() / 10), 2);
    },
    SSS: function (dateObj) { return pad(dateObj.getMilliseconds(), 3); },
    a: function (dateObj, i18n) {
        return dateObj.getHours() < 12 ? i18n.amPm[0] : i18n.amPm[1];
    },
    A: function (dateObj, i18n) {
        return dateObj.getHours() < 12
            ? i18n.amPm[0].toUpperCase()
            : i18n.amPm[1].toUpperCase();
    },
    ZZ: function (dateObj) {
        var offset = dateObj.getTimezoneOffset();
        return ((offset > 0 ? "-" : "+") +
            pad(Math.floor(Math.abs(offset) / 60) * 100 + (Math.abs(offset) % 60), 4));
    },
    Z: function (dateObj) {
        var offset = dateObj.getTimezoneOffset();
        return ((offset > 0 ? "-" : "+") +
            pad(Math.floor(Math.abs(offset) / 60), 2) +
            ":" +
            pad(Math.abs(offset) % 60, 2));
    }
};
var monthParse = function (v) { return +v - 1; };
var emptyDigits = [null, twoDigitsOptional];
var emptyWord = [null, word];
var amPm = [
    "isPm",
    word,
    function (v, i18n) {
        var val = v.toLowerCase();
        if (val === i18n.amPm[0]) {
            return 0;
        }
        else if (val === i18n.amPm[1]) {
            return 1;
        }
        return null;
    }
];
var timezoneOffset = [
    "timezoneOffset",
    "[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",
    function (v) {
        var parts = (v + "").match(/([+-]|\d\d)/gi);
        if (parts) {
            var minutes = +parts[1] * 60 + parseInt(parts[2], 10);
            return parts[0] === "+" ? minutes : -minutes;
        }
        return 0;
    }
];
var parseFlags = {
    D: ["day", twoDigitsOptional],
    DD: ["day", twoDigits],
    Do: ["day", twoDigitsOptional + word, function (v) { return parseInt(v, 10); }],
    M: ["month", twoDigitsOptional, monthParse],
    MM: ["month", twoDigits, monthParse],
    YY: [
        "year",
        twoDigits,
        function (v) {
            var now = new Date();
            var cent = +("" + now.getFullYear()).substr(0, 2);
            return +("" + (+v > 68 ? cent - 1 : cent) + v);
        }
    ],
    h: ["hour", twoDigitsOptional, undefined, "isPm"],
    hh: ["hour", twoDigits, undefined, "isPm"],
    H: ["hour", twoDigitsOptional],
    HH: ["hour", twoDigits],
    m: ["minute", twoDigitsOptional],
    mm: ["minute", twoDigits],
    s: ["second", twoDigitsOptional],
    ss: ["second", twoDigits],
    YYYY: ["year", fourDigits],
    S: ["millisecond", "\\d", function (v) { return +v * 100; }],
    SS: ["millisecond", twoDigits, function (v) { return +v * 10; }],
    SSS: ["millisecond", threeDigits],
    d: emptyDigits,
    dd: emptyDigits,
    ddd: emptyWord,
    dddd: emptyWord,
    MMM: ["month", word, monthUpdate("monthNamesShort")],
    MMMM: ["month", word, monthUpdate("monthNames")],
    a: amPm,
    A: amPm,
    ZZ: timezoneOffset,
    Z: timezoneOffset
};
// Some common format strings
var globalMasks = {
    default: "ddd MMM DD YYYY HH:mm:ss",
    shortDate: "M/D/YY",
    mediumDate: "MMM D, YYYY",
    longDate: "MMMM D, YYYY",
    fullDate: "dddd, MMMM D, YYYY",
    isoDate: "YYYY-MM-DD",
    isoDateTime: "YYYY-MM-DDTHH:mm:ssZ",
    shortTime: "HH:mm",
    mediumTime: "HH:mm:ss",
    longTime: "HH:mm:ss.SSS"
};
var setGlobalDateMasks = function (masks) { return assign(globalMasks, masks); };
/***
 * Format a date
 * @method format
 * @param {Date|number} dateObj
 * @param {string} mask Format of the date, i.e. 'mm-dd-yy' or 'shortDate'
 * @returns {string} Formatted date string
 */
var format = function (dateObj, mask, i18n) {
    if (mask === void 0) { mask = globalMasks["default"]; }
    if (i18n === void 0) { i18n = {}; }
    if (typeof dateObj === "number") {
        dateObj = new Date(dateObj);
    }
    if (Object.prototype.toString.call(dateObj) !== "[object Date]" ||
        isNaN(dateObj.getTime())) {
        throw new Error("Invalid Date pass to format");
    }
    mask = globalMasks[mask] || mask;
    var literals = [];
    // Make literals inactive by replacing them with @@@
    mask = mask.replace(literal, function ($0, $1) {
        literals.push($1);
        return "@@@";
    });
    var combinedI18nSettings = assign(assign({}, globalI18n), i18n);
    // Apply formatting rules
    mask = mask.replace(token, function ($0) {
        return formatFlags[$0](dateObj, combinedI18nSettings);
    });
    // Inline literal values back into the formatted value
    return mask.replace(/@@@/g, function () { return literals.shift(); });
};
/**
 * Parse a date string into a Javascript Date object /
 * @method parse
 * @param {string} dateStr Date string
 * @param {string} format Date parse format
 * @param {i18n} I18nSettingsOptional Full or subset of I18N settings
 * @returns {Date|null} Returns Date object. Returns null what date string is invalid or doesn't match format
 */
function parse(dateStr, format, i18n) {
    if (i18n === void 0) { i18n = {}; }
    if (typeof format !== "string") {
        throw new Error("Invalid format in fecha parse");
    }
    // Check to see if the format is actually a mask
    format = globalMasks[format] || format;
    // Avoid regular expression denial of service, fail early for really long strings
    // https://www.owasp.org/index.php/Regular_expression_Denial_of_Service_-_ReDoS
    if (dateStr.length > 1000) {
        return null;
    }
    // Default to the beginning of the year.
    var today = new Date();
    var dateInfo = {
        year: today.getFullYear(),
        month: 0,
        day: 1,
        hour: 0,
        minute: 0,
        second: 0,
        millisecond: 0,
        isPm: null,
        timezoneOffset: null
    };
    var parseInfo = [];
    var literals = [];
    // Replace all the literals with @@@. Hopefully a string that won't exist in the format
    var newFormat = format.replace(literal, function ($0, $1) {
        literals.push(regexEscape($1));
        return "@@@";
    });
    var specifiedFields = {};
    var requiredFields = {};
    // Change every token that we find into the correct regex
    newFormat = regexEscape(newFormat).replace(token, function ($0) {
        var info = parseFlags[$0];
        var field = info[0], regex = info[1], requiredField = info[3];
        // Check if the person has specified the same field twice. This will lead to confusing results.
        if (specifiedFields[field]) {
            throw new Error("Invalid format. " + field + " specified twice in format");
        }
        specifiedFields[field] = true;
        // Check if there are any required fields. For instance, 12 hour time requires AM/PM specified
        if (requiredField) {
            requiredFields[requiredField] = true;
        }
        parseInfo.push(info);
        return "(" + regex + ")";
    });
    // Check all the required fields are present
    Object.keys(requiredFields).forEach(function (field) {
        if (!specifiedFields[field]) {
            throw new Error("Invalid format. " + field + " is required in specified format");
        }
    });
    // Add back all the literals after
    newFormat = newFormat.replace(/@@@/g, function () { return literals.shift(); });
    // Check if the date string matches the format. If it doesn't return null
    var matches = dateStr.match(new RegExp(newFormat, "i"));
    if (!matches) {
        return null;
    }
    var combinedI18nSettings = assign(assign({}, globalI18n), i18n);
    // For each match, call the parser function for that date part
    for (var i = 1; i < matches.length; i++) {
        var _a = parseInfo[i - 1], field = _a[0], parser = _a[2];
        var value = parser
            ? parser(matches[i], combinedI18nSettings)
            : +matches[i];
        // If the parser can't make sense of the value, return null
        if (value == null) {
            return null;
        }
        dateInfo[field] = value;
    }
    if (dateInfo.isPm === 1 && dateInfo.hour != null && +dateInfo.hour !== 12) {
        dateInfo.hour = +dateInfo.hour + 12;
    }
    else if (dateInfo.isPm === 0 && +dateInfo.hour === 12) {
        dateInfo.hour = 0;
    }
    var dateWithoutTZ = new Date(dateInfo.year, dateInfo.month, dateInfo.day, dateInfo.hour, dateInfo.minute, dateInfo.second, dateInfo.millisecond);
    var validateFields = [
        ["month", "getMonth"],
        ["day", "getDate"],
        ["hour", "getHours"],
        ["minute", "getMinutes"],
        ["second", "getSeconds"]
    ];
    for (var i = 0, len = validateFields.length; i < len; i++) {
        // Check to make sure the date field is within the allowed range. Javascript dates allows values
        // outside the allowed range. If the values don't match the value was invalid
        if (specifiedFields[validateFields[i][0]] &&
            dateInfo[validateFields[i][0]] !== dateWithoutTZ[validateFields[i][1]]()) {
            return null;
        }
    }
    if (dateInfo.timezoneOffset == null) {
        return dateWithoutTZ;
    }
    return new Date(Date.UTC(dateInfo.year, dateInfo.month, dateInfo.day, dateInfo.hour, dateInfo.minute - dateInfo.timezoneOffset, dateInfo.second, dateInfo.millisecond));
}
var fecha = {
    format: format,
    parse: parse,
    defaultI18n: defaultI18n,
    setGlobalDateI18n: setGlobalDateI18n,
    setGlobalDateMasks: setGlobalDateMasks
};

function t(e){var t=e.split(":").map(Number);return 3600*t[0]+60*t[1]+t[2]}var a=function(){try{(new Date).toLocaleDateString("i");}catch(e){return "RangeError"===e.name}return !1}()?function(e,t){return e.toLocaleDateString(t.language,{year:"numeric",month:"long",day:"numeric"})}:function(t){return fecha.format(t,"mediumDate")},r=function(){try{(new Date).toLocaleString("i");}catch(e){return "RangeError"===e.name}return !1}()?function(e,t){return e.toLocaleString(t.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"})}:function(t){return fecha.format(t,"haDateTime")},n=function(){try{(new Date).toLocaleTimeString("i");}catch(e){return "RangeError"===e.name}return !1}()?function(e,t){return e.toLocaleTimeString(t.language,{hour:"numeric",minute:"2-digit"})}:function(t){return fecha.format(t,"shortTime")},s=[60,60,24,7],i=["second","minute","hour","day"];function o(e,t,a){void 0===a&&(a={});var r,n=((a.compareTime||new Date).getTime()-e.getTime())/1e3,o=!1===a.includeTense?"duration":(n>=0?"past":"future")+"_duration";n=Math.abs(n);for(var c=0;c<s.length;c++){if(n<s[c]){n=Math.floor(n),r=t("ui.components.relative_time."+o+"."+i[c],"count",n);break}n/=s[c];}return void 0===r&&(r=t("ui.components.relative_time."+o+".week","count",n=Math.floor(n))),r}var c=function(e){return e<10?"0"+e:e};function u(e){var t=Math.floor(e/3600),a=Math.floor(e%3600/60),r=Math.floor(e%3600%60);return t>0?t+":"+c(a)+":"+c(r):a>0?a+":"+c(r):r>0?""+r:null}function l(e){var a=t(e.attributes.remaining);if("active"===e.state){var r=(new Date).getTime(),n=new Date(e.last_changed).getTime();a=Math.max(a-(r-n)/1e3,0);}return a}function h(){return (h=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var a=arguments[t];for(var r in a)Object.prototype.hasOwnProperty.call(a,r)&&(e[r]=a[r]);}return e}).apply(this,arguments)}var m,f,d=function(e,t,a,r){void 0===r&&(r=!1),e._themes||(e._themes={});var n=t.default_theme;("default"===a||a&&t.themes[a])&&(n=a);var s=h({},e._themes);if("default"!==n){var i=t.themes[n];Object.keys(i).forEach(function(t){var a="--"+t;e._themes[a]="",s[a]=i[t];});}if(e.updateStyles?e.updateStyles(s):window.ShadyCSS&&window.ShadyCSS.styleSubtree(e,s),r){var o=document.querySelector("meta[name=theme-color]");if(o){o.hasAttribute("default-content")||o.setAttribute("default-content",o.getAttribute("content"));var c=s["--primary-color"]||o.getAttribute("default-content");o.setAttribute("content",c);}}},p=function(e){return "function"==typeof e.getCardSize?e.getCardSize():4};function g(e){return e.substr(0,e.indexOf("."))}function b(e){return e.substr(e.indexOf(".")+1)}function v(e){var t=e.locale.language||"en";return e.translationMetadata.translations[t]&&e.translationMetadata.translations[t].isRTL||!1}function _(e){return v(e)?"rtl":"ltr"}function y(e){return g(e.entity_id)}!function(e){e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.space_comma="space_comma",e.none="none";}(m||(m={})),function(e){e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24";}(f||(f={}));var w=function(e,t,a){var r;switch(null==t?void 0:t.number_format){case m.comma_decimal:r=["en-US","en"];break;case m.decimal_comma:r=["de","es","it"];break;case m.space_comma:r=["fr","sv","cs"];break;case m.system:r=void 0;break;default:r=null==t?void 0:t.language;}if(Number.isNaN=Number.isNaN||function e(t){return "number"==typeof t&&e(t)},!Number.isNaN(Number(e))&&Intl&&(null==t?void 0:t.number_format)!==m.none)try{return new Intl.NumberFormat(r,k(e,a)).format(Number(e))}catch(t){return console.error(t),new Intl.NumberFormat(void 0,k(e,a)).format(Number(e))}return e?e.toString():""},k=function(e,t){var a=t||{};if("string"!=typeof e)return a;if(!t||!t.minimumFractionDigits&&!t.maximumFractionDigits){var r=e.indexOf(".")>-1?e.split(".")[1].length:0;a.minimumFractionDigits=r,a.maximumFractionDigits=r;}return a};function S(e,t,s,i){var o=void 0!==i?i:t.state;if("unknown"===o||"unavailable"===o)return e("state.default."+o);if(t.attributes.unit_of_measurement)return w(o,s)+" "+t.attributes.unit_of_measurement;var c=y(t);if("input_datetime"===c){var u;if(!t.attributes.has_time)return u=new Date(t.attributes.year,t.attributes.month-1,t.attributes.day),a(u,s);if(!t.attributes.has_date){var l=new Date;return u=new Date(l.getFullYear(),l.getMonth(),l.getDay(),t.attributes.hour,t.attributes.minute),n(u,s)}return u=new Date(t.attributes.year,t.attributes.month-1,t.attributes.day,t.attributes.hour,t.attributes.minute),r(u,s)}return "humidifier"===c&&"on"===o&&t.attributes.humidity?t.attributes.humidity+" %":"counter"===c||"number"===c?w(o,s):t.attributes.device_class&&e("component."+c+".state."+t.attributes.device_class+"."+t.state)||e("component."+c+".state._."+t.state)||t.state}var x="hass:bookmark",D="lovelace",N=["climate","cover","configurator","input_select","input_number","input_text","lock","media_player","scene","script","timer","vacuum","water_heater","weblink"],T=["alarm_control_panel","automation","camera","climate","configurator","cover","fan","group","history_graph","input_datetime","light","lock","media_player","script","sun","updater","vacuum","water_heater","weather"],E=["input_number","input_select","input_text","scene","weblink"],M=["camera","configurator","history_graph","scene"],F=["closed","locked","off"],q=new Set(["fan","input_boolean","light","switch","group","automation"]),C="°C",O="°F",R="group.default_view",A=function(e,t,a,r){r=r||{},a=null==a?{}:a;var n=new Event(t,{bubbles:void 0===r.bubbles||r.bubbles,cancelable:Boolean(r.cancelable),composed:void 0===r.composed||r.composed});return n.detail=a,e.dispatchEvent(n),n},L=new Set(["call-service","divider","section","weblink","cast","select"]),I={alert:"toggle",automation:"toggle",climate:"climate",cover:"cover",fan:"toggle",group:"group",input_boolean:"toggle",input_number:"input-number",input_select:"input-select",input_text:"input-text",light:"toggle",lock:"lock",media_player:"media-player",remote:"toggle",scene:"scene",script:"script",sensor:"sensor",timer:"timer",switch:"toggle",vacuum:"toggle",water_heater:"climate",input_datetime:"input-datetime"},j=function(e,t){void 0===t&&(t=!1);var a=function(e,t){return r("hui-error-card",{type:"error",error:e,config:t})},r=function(e,t){var r=window.document.createElement(e);try{r.setConfig(t);}catch(r){return console.error(e,r),a(r.message,t)}return r};if(!e||"object"!=typeof e||!t&&!e.type)return a("No type defined",e);var n=e.type;if(n&&n.startsWith("custom:"))n=n.substr("custom:".length);else if(t)if(L.has(n))n="hui-"+n+"-row";else {if(!e.entity)return a("Invalid config given.",e);var s=e.entity.split(".",1)[0];n="hui-"+(I[s]||"text")+"-entity-row";}else n="hui-"+n+"-card";if(customElements.get(n))return r(n,e);var i=a("Custom element doesn't exist: "+e.type+".",e);i.style.display="None";var o=setTimeout(function(){i.style.display="";},2e3);return customElements.whenDefined(e.type).then(function(){clearTimeout(o),A(i,"ll-rebuild",{},i);}),i},z=function(e,t,a){var r;return void 0===a&&(a=!1),function(){var n=[].slice.call(arguments),s=this,i=function(){r=null,a||e.apply(s,n);},o=a&&!r;clearTimeout(r),r=setTimeout(i,t),o&&e.apply(s,n);}},U={alert:"hass:alert",automation:"hass:playlist-play",calendar:"hass:calendar",camera:"hass:video",climate:"hass:thermostat",configurator:"hass:settings",conversation:"hass:text-to-speech",device_tracker:"hass:account",fan:"hass:fan",group:"hass:google-circles-communities",history_graph:"hass:chart-line",homeassistant:"hass:home-assistant",homekit:"hass:home-automation",image_processing:"hass:image-filter-frames",input_boolean:"hass:drawing",input_datetime:"hass:calendar-clock",input_number:"hass:ray-vertex",input_select:"hass:format-list-bulleted",input_text:"hass:textbox",light:"hass:lightbulb",mailbox:"hass:mailbox",notify:"hass:comment-alert",person:"hass:account",plant:"hass:flower",proximity:"hass:apple-safari",remote:"hass:remote",scene:"hass:google-pages",script:"hass:file-document",sensor:"hass:eye",simple_alarm:"hass:bell",sun:"hass:white-balance-sunny",switch:"hass:flash",timer:"hass:timer",updater:"hass:cloud-upload",vacuum:"hass:robot-vacuum",water_heater:"hass:thermometer",weblink:"hass:open-in-new"};function B(e,t){if(e in U)return U[e];switch(e){case"alarm_control_panel":switch(t){case"armed_home":return "hass:bell-plus";case"armed_night":return "hass:bell-sleep";case"disarmed":return "hass:bell-outline";case"triggered":return "hass:bell-ring";default:return "hass:bell"}case"binary_sensor":return t&&"off"===t?"hass:radiobox-blank":"hass:checkbox-marked-circle";case"cover":return "closed"===t?"hass:window-closed":"hass:window-open";case"lock":return t&&"unlocked"===t?"hass:lock-open":"hass:lock";case"media_player":return t&&"off"!==t&&"idle"!==t?"hass:cast-connected":"hass:cast";case"zwave":switch(t){case"dead":return "hass:emoticon-dead";case"sleeping":return "hass:sleep";case"initializing":return "hass:timer-sand";default:return "hass:z-wave"}default:return console.warn("Unable to find icon for domain "+e+" ("+t+")"),"hass:bookmark"}}var P=function(e,t){var a=t.value||t,r=t.attribute?e.attributes[t.attribute]:e.state;switch(t.operator||"=="){case"==":return r===a;case"<=":return r<=a;case"<":return r<a;case">=":return r>=a;case">":return r>a;case"!=":return r!==a;case"regex":return r.match(a);default:return !1}},V=function(e){A(window,"haptic",e);},W=function(e,t,a){void 0===a&&(a=!1),a?history.replaceState(null,"",t):history.pushState(null,"",t),A(window,"location-changed",{replace:a});},Y=function(e,t,a){void 0===a&&(a=!0);var r,n=g(t),s="group"===n?"homeassistant":n;switch(n){case"lock":r=a?"unlock":"lock";break;case"cover":r=a?"open_cover":"close_cover";break;default:r=a?"turn_on":"turn_off";}return e.callService(s,r,{entity_id:t})},G=function(e,t){var a=F.includes(e.states[t].state);return Y(e,t,a)},H=function(e,t,a,r){if(r||(r={action:"more-info"}),!r.confirmation||r.confirmation.exemptions&&r.confirmation.exemptions.some(function(e){return e.user===t.user.id})||(V("warning"),confirm(r.confirmation.text||"Are you sure you want to "+r.action+"?")))switch(r.action){case"more-info":(a.entity||a.camera_image)&&A(e,"hass-more-info",{entityId:a.entity?a.entity:a.camera_image});break;case"navigate":r.navigation_path&&W(0,r.navigation_path);break;case"url":r.url_path&&window.open(r.url_path);break;case"toggle":a.entity&&(G(t,a.entity),V("success"));break;case"call-service":if(!r.service)return void V("failure");var n=r.service.split(".",2);t.callService(n[0],n[1],r.service_data),V("success");break;case"fire-dom-event":A(e,"ll-custom",r);}},J=function(e,t,a,r){var n;"double_tap"===r&&a.double_tap_action?n=a.double_tap_action:"hold"===r&&a.hold_action?n=a.hold_action:"tap"===r&&a.tap_action&&(n=a.tap_action),H(e,t,a,n);},K=function(e,t,a,r,n){var s;if(n&&a.double_tap_action?s=a.double_tap_action:r&&a.hold_action?s=a.hold_action:!r&&a.tap_action&&(s=a.tap_action),s||(s={action:"more-info"}),!s.confirmation||s.confirmation.exemptions&&s.confirmation.exemptions.some(function(e){return e.user===t.user.id})||confirm(s.confirmation.text||"Are you sure you want to "+s.action+"?"))switch(s.action){case"more-info":(s.entity||a.entity||a.camera_image)&&(A(e,"hass-more-info",{entityId:s.entity?s.entity:a.entity?a.entity:a.camera_image}),s.haptic&&V(s.haptic));break;case"navigate":s.navigation_path&&(W(0,s.navigation_path),s.haptic&&V(s.haptic));break;case"url":s.url_path&&window.open(s.url_path),s.haptic&&V(s.haptic);break;case"toggle":a.entity&&(G(t,a.entity),s.haptic&&V(s.haptic));break;case"call-service":if(!s.service)return;var i=s.service.split(".",2),o=i[0],c=i[1],u=h({},s.service_data);"entity"===u.entity_id&&(u.entity_id=a.entity),t.callService(o,c,u),s.haptic&&V(s.haptic);break;case"fire-dom-event":A(e,"ll-custom",s),s.haptic&&V(s.haptic);}};function Q(e){return void 0!==e&&"none"!==e.action}function X(e,t,a){if(t.has("config")||a)return !0;if(e.config.entity){var r=t.get("hass");return !r||r.states[e.config.entity]!==e.hass.states[e.config.entity]}return !1}function Z(e){return void 0!==e&&"none"!==e.action}var $=function(e,t,a){void 0===a&&(a=!0);var r={};t.forEach(function(t){if(F.includes(e.states[t].state)===a){var n=g(t),s=["cover","lock"].includes(n)?n:"homeassistant";s in r||(r[s]=[]),r[s].push(t);}}),Object.keys(r).forEach(function(t){var n;switch(t){case"lock":n=a?"unlock":"lock";break;case"cover":n=a?"open_cover":"close_cover";break;default:n=a?"turn_on":"turn_off";}e.callService(t,n,{entity_id:r[t]});});},ee=function(){var e=document.querySelector("home-assistant");if(e=(e=(e=(e=(e=(e=(e=(e=e&&e.shadowRoot)&&e.querySelector("home-assistant-main"))&&e.shadowRoot)&&e.querySelector("app-drawer-layout partial-panel-resolver"))&&e.shadowRoot||e)&&e.querySelector("ha-panel-lovelace"))&&e.shadowRoot)&&e.querySelector("hui-root")){var t=e.lovelace;return t.current_view=e.___curView,t}return null},te={humidity:"hass:water-percent",illuminance:"hass:brightness-5",temperature:"hass:thermometer",pressure:"hass:gauge",power:"hass:flash",signal_strength:"hass:wifi"},ae={binary_sensor:function(e){var t=e.state&&"off"===e.state;switch(e.attributes.device_class){case"battery":return t?"hass:battery":"hass:battery-outline";case"cold":return t?"hass:thermometer":"hass:snowflake";case"connectivity":return t?"hass:server-network-off":"hass:server-network";case"door":return t?"hass:door-closed":"hass:door-open";case"garage_door":return t?"hass:garage":"hass:garage-open";case"gas":case"power":case"problem":case"safety":case"smoke":return t?"hass:shield-check":"hass:alert";case"heat":return t?"hass:thermometer":"hass:fire";case"light":return t?"hass:brightness-5":"hass:brightness-7";case"lock":return t?"hass:lock":"hass:lock-open";case"moisture":return t?"hass:water-off":"hass:water";case"motion":return t?"hass:walk":"hass:run";case"occupancy":return t?"hass:home-outline":"hass:home";case"opening":return t?"hass:square":"hass:square-outline";case"plug":return t?"hass:power-plug-off":"hass:power-plug";case"presence":return t?"hass:home-outline":"hass:home";case"sound":return t?"hass:music-note-off":"hass:music-note";case"vibration":return t?"hass:crop-portrait":"hass:vibrate";case"window":return t?"hass:window-closed":"hass:window-open";default:return t?"hass:radiobox-blank":"hass:checkbox-marked-circle"}},cover:function(e){var t="closed"!==e.state;switch(e.attributes.device_class){case"garage":return t?"hass:garage-open":"hass:garage";case"door":return t?"hass:door-open":"hass:door-closed";case"shutter":return t?"hass:window-shutter-open":"hass:window-shutter";case"blind":return t?"hass:blinds-open":"hass:blinds";case"window":return t?"hass:window-open":"hass:window-closed";default:return B("cover",e.state)}},sensor:function(e){var t=e.attributes.device_class;if(t&&t in te)return te[t];if("battery"===t){var a=Number(e.state);if(isNaN(a))return "hass:battery-unknown";var r=10*Math.round(a/10);return r>=100?"hass:battery":r<=0?"hass:battery-alert":"hass:battery-"+r}var n=e.attributes.unit_of_measurement;return "°C"===n||"°F"===n?"hass:thermometer":B("sensor")},input_datetime:function(e){return e.attributes.has_date?e.attributes.has_time?B("input_datetime"):"hass:calendar":"hass:clock"}},re=function(e){if(!e)return "hass:bookmark";if(e.attributes.icon)return e.attributes.icon;var t=g(e.entity_id);return t in ae?ae[t](e):B(t,e.state)};

const CARD_VERSION = '1.3.6';

/* eslint no-console: 0 */
console.info(`%c  CONFIG-TEMPLATE-CARD  \n%c  Version ${CARD_VERSION}         `, 'color: orange; font-weight: bold; background: black', 'color: white; font-weight: bold; background: dimgray');
let ConfigTemplateCard = class ConfigTemplateCard extends n$2 {
    constructor() {
        super(...arguments);
        this._initialized = false;
    }
    setConfig(config) {
        if (!config) {
            throw new Error('Invalid configuration');
        }
        if (!config.card && !config.row && !config.element) {
            throw new Error('No card or row or element defined');
        }
        if (config.card && !config.card.type) {
            throw new Error('No card type defined');
        }
        if (config.card && config.card.type === 'picture-elements') {
            console.warn('WARNING: config-template-card should not be used with the picture-elements card itself. Instead use it as one of the elements. Check the README for details');
        }
        if (config.element && !config.element.type) {
            throw new Error('No element type defined');
        }
        if (!config.entities) {
            throw new Error('No entities defined');
        }
        this._config = config;
        this.loadCardHelpers();
    }
    shouldUpdate(changedProps) {
        if (!this._initialized) {
            this._initialize();
        }
        if (changedProps.has('_config')) {
            return true;
        }
        if (this._config) {
            const oldHass = changedProps.get('hass');
            if (oldHass) {
                for (const entity of this._config.entities) {
                    const evaluatedTemplate = this._evaluateTemplate(entity);
                    if (Boolean(this.hass && oldHass.states[evaluatedTemplate] !== this.hass.states[evaluatedTemplate])) {
                        return true;
                    }
                }
                return false;
            }
        }
        return true;
    }
    getCardSize() {
        if (this.shadowRoot) {
            const element = this.shadowRoot.querySelector('#card > *');
            if (element) {
                console.log('computeCardSize is ' + p(element));
                return p(element);
            }
        }
        return 1;
    }
    render() {
        if (!this._config ||
            !this.hass ||
            !this._helpers ||
            (!this._config.card && !this._config.row && !this._config.element)) {
            return y$1 ``;
        }
        let config = this._config.card
            ? deepcopy(this._config.card)
            : this._config.row
                ? deepcopy(this._config.row)
                : deepcopy(this._config.element);
        let style = this._config.style ? deepcopy(this._config.style) : {};
        config = this._evaluateConfig(config);
        if (style) {
            style = this._evaluateConfig(style);
        }
        const element = this._config.card
            ? this._helpers.createCardElement(config)
            : this._config.row
                ? this._helpers.createRowElement(config)
                : this._helpers.createHuiElement(config);
        element.hass = this.hass;
        if (this._config.element) {
            if (style) {
                Object.keys(style).forEach(prop => {
                    this.style.setProperty(prop, style[prop]);
                });
            }
            if (config.style) {
                Object.keys(config.style).forEach(prop => {
                    element.style.setProperty(prop, config.style[prop]);
                });
            }
        }
        return y$1 `
      <div id="card">
        ${element}
      </div>
    `;
    }
    _initialize() {
        if (this.hass === undefined)
            return;
        if (this._config === undefined)
            return;
        if (this._helpers === undefined)
            return;
        this._initialized = true;
    }
    async loadCardHelpers() {
        this._helpers = await window.loadCardHelpers();
    }
    /* eslint-disable @typescript-eslint/no-explicit-any */
    _evaluateConfig(config) {
        Object.entries(config).forEach(entry => {
            const key = entry[0];
            const value = entry[1];
            if (value !== null) {
                if (value instanceof Array) {
                    config[key] = this._evaluateArray(value);
                }
                else if (typeof value === 'object') {
                    config[key] = this._evaluateConfig(value);
                }
                else if (typeof value === 'string' && value.includes('${')) {
                    config[key] = this._evaluateTemplate(value);
                }
            }
        });
        return config;
    }
    /* eslint-disable @typescript-eslint/no-explicit-any */
    _evaluateArray(array) {
        for (let i = 0; i < array.length; ++i) {
            const value = array[i];
            if (value instanceof Array) {
                array[i] = this._evaluateArray(value);
            }
            else if (typeof value === 'object') {
                array[i] = this._evaluateConfig(value);
            }
            else if (typeof value === 'string' && value.includes('${')) {
                array[i] = this._evaluateTemplate(value);
            }
        }
        return array;
    }
    _evaluateTemplate(template) {
        if (!template.includes('${')) {
            return template;
        }
        /* eslint-disable @typescript-eslint/no-unused-vars */
        const user = this.hass ? this.hass.user : undefined;
        const states = this.hass ? this.hass.states : undefined;
        let vars;
        let varDef = '';
        if (this._config) {
            if (Array.isArray(this._config.variables)) {
                // if variables are an array, create vars as an array
                vars = [];
                for (const v in this._config.variables) {
                    const newV = eval(this._config.variables[v]);
                    vars.push(newV);
                }
            }
            else {
                // if it is an object, then create a key-value map containing
                // the values
                vars = {};
                for (const varName in this._config.variables) {
                    const newV = eval(this._config.variables[varName]);
                    vars[varName] = newV;
                    // create variable definitions to be injected:
                    varDef = varDef + `var ${varName} = vars['${varName}'];\n`;
                }
            }
        }
        return eval(varDef + template.substring(2, template.length - 1));
    }
};
__decorate([
    e$3({ attribute: false })
], ConfigTemplateCard.prototype, "hass", void 0);
__decorate([
    t$1()
], ConfigTemplateCard.prototype, "_config", void 0);
__decorate([
    t$1()
], ConfigTemplateCard.prototype, "_helpers", void 0);
ConfigTemplateCard = __decorate([
    n$1('config-template-card')
], ConfigTemplateCard);

export { ConfigTemplateCard };
