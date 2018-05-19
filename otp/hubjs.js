

/*closure*/


/*
            http://closure-compiler.appspot.com/home
            // ==ClosureCompiler==
             @compilation_level ADVANCED_OPTIMIZATIONS
             @output_file_name default.js
             @externs_url http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.js
             @formatting pretty_print
            ==/ClosureCompiler==
 */
//jsdoc
//http://code.google.com/p/jsdoc-toolkit/wiki
//https://github.com/douglascrockford/JSON-js/blob/master/json2.js
//http://bestiejs.github.com/json3/
/*
HubJS
    {static function}
        -namespace
        -constant
    {class}
        -ui
            -SegmentedControl
            -Scroll
            -Swipe
            -ListView
            -Loading
            -Dialog

        -Validation
        -Touch
        -crypto
            -MD5
        -native
            -camera..?phonegap 참조
        -Util

 */

/**
 * Com2uS Hub's Main Object
 * @static
 */
var HubJS = HubJS || {};

/**
 * Define namespace
 * @static
 * @param {String} namespace's string
 */
HubJS.namespace = function(ns_string){
    var parts = ns_string.split('.');
    var parent = HubJS;
    var i;

    if(parts[0]==='HubJS'){
        parts = parts.slice(1);
    }
    for(i = 0 ; i < parts.length; i+=1){
        if(typeof parent[parts[i]]==='undefined'){
            parent[parts[i]] = {};
        }
        parent = parent[parts[i]];
    }
    return parent;
}

/**
 * Define constant
 * @static
 */
HubJS.constant = (function(){
    var constants = {};
    var ownProp = Object.prototype.hasOwnProperty;
    var allowed = {
        'string' : 1,
        'number' : 1,
        'boolean' :1
    };//
    var prefix = (Math.random()+'_').slice(2);
    return {
        /** Set constant name-value pair */
        set : function(name, value){
            if(this.isDefined(name)){
                return false;
            }
            if(!ownProp.call(allowed, typeof value)){
                return false;
            }
            constants[prefix+name] = value;
            return true;
        },
        /** Get boolean of whether name is defined  */
        isDefined : function(name){
            return ownProp.call(constants, prefix+name);
        },
        /** Get value of name */
        get: function(name){
            if(this.isDefined(name)){
                return constants[prefix+name];
            }
            return null;
        }
    };
}());

/**
 * Log : if 'IS_DEFINE', will...
 * @static
 */
HubJS.constant.set('IS_DEBUG', true);
HubJS.log = function(message){
    var isDebug = HubJS.constant.get('IS_DEBUG');
    if(isDebug){
        console.log(message);
    }else{

    }
};

/**
 * Validation email, password, hubid, tel, HTML, URL, IP
 * @class Validation
 * @example
 * var validation = new HubJS.Validation();
 * var ret = validation.validate('email','pomtech@com2us.com');
 *
 */
HubJS.namespace('HubJS.Validation');

HubJS.Validation = function(){
    this._type = {
        'email' : 'HubJS.Validation.Email'
        ,
        'password':'HubJS.Validation.Password'
        ,
        'hubid':'HubJS.Validation.HubId'
        ,
        'tel':'HubJS.Validation.Tel'
    };
}

HubJS.Validation.prototype.validate = function(type, value){
    try{
        var validationObj = eval("new " + this._type[type] + "()");
        var ret = validationObj.isValid(value);
        return ret;
    }catch(e){
        return false;
    }
}

/**
 * (Private Class)Email Validation
 * @class Email
 */
HubJS.namespace('HubJS.Validation.Email');

HubJS.Validation.Email = function(){
    this.rx = /^(([\w\-]+\.)+[\w\-]+|([a-zA-Z]{1}|[\w\-]{2,}))@((([0-1]?[0-9]{1,2}|25[0-5]|2[0-4][0-9])\.([0-1]?[0-9]{1,2}|25[0-5]|2[0-4][0-9])\.([0-1]?[0-9]{1,2}|25[0-5]|2[0-4][0-9])\.([0-1]?[0-9]{1,2}|25[0-5]|2[0-4][0-9])){1}|([a-zA-Z]+[\w\-]+\.)+[a-zA-Z]{2,4})$/
}
HubJS.Validation.Email.prototype.isValid = function(value){
    if(this.rx.test(value)) {
        return true;
    } else {
        return false;
    }
}

/**
 * (Private Class)Password Validation
 * 4~25, 0~9|a~z|A~Z|-_+.@
 * @class Password
 */
HubJS.namespace('HubJS.Validation.Password');

HubJS.Validation.Password = function(){
    //4~12 not allowed special character except . - _ +
    this.rx = /^[a-zA-Z0-9\.\-\_\+]{4,12}$/
}
HubJS.Validation.Password.prototype.isValid = function(value){
    if(this.rx.test(value)) {
        return true;
    } else {
        return false;
    }
}

/**
 * (Private Class)HubId Validation
 * 4~12, not white space, 0~9|a~z|A~Z|-_.
 * @class HubId
 */
HubJS.namespace('HubJS.Validation.HubId');

HubJS.Validation.HubId = function(){
    this.rx = /^[a-zA-Z0-9\.\-\_]{4,9}$/
}
HubJS.Validation.HubId.prototype.isValid = function(value){
    if(this.rx.test(value)) {
        return true;
    } else {
        return false;
    }
}



/**
 *
 * @class MD5
 * @example
 * var md5 = new HubJS.crypto.MD5();
 * var md5_string = md5.getHex('aaaa');
 */
HubJS.namespace('HubJS.crypto.MD5');
HubJS.crypto.MD5 = function(){
    this.hexcase = 0;  /* hex output format. 0 - lowercase; 1 - uppercase        */
    this.b64pad  = ""; /* base-64 pad character. "=" for strict RFC compliance   */
    this.chrsz   = 8;  /* bits per input character. 8 - ASCII; 16 - Unicode      */
}
HubJS.crypto.MD5.prototype.getHex = function(input_string){
    var s = input_string;
    return this.binl2hex(this.core_md5(this.str2binl(s), s.length * this.chrsz));
}
HubJS.crypto.MD5.prototype.str2binl = function(str)
{
    var bin = Array();
    var mask = (1 << this.chrsz) - 1;
    for(var i = 0; i < str.length * this.chrsz; i += this.chrsz)
        bin[i>>5] |= (str.charCodeAt(i / this.chrsz) & mask) << (i%32);
    return bin;
}
/*
 * Calculate the MD5 of an array of little-endian words, and a bit length
 */
HubJS.crypto.MD5.prototype.core_md5 = function(x, len)
{
    /* append padding */
    x[len >> 5] |= 0x80 << ((len) % 32);
    x[(((len + 64) >>> 9) << 4) + 14] = len;

    var a =  1732584193;
    var b = -271733879;
    var c = -1732584194;
    var d =  271733878;

    for(var i = 0; i < x.length; i += 16)
    {
        var olda = a;
        var oldb = b;
        var oldc = c;
        var oldd = d;

        a = this.md5_ff(a, b, c, d, x[i+ 0], 7 , -680876936);
        d = this.md5_ff(d, a, b, c, x[i+ 1], 12, -389564586);
        c = this.md5_ff(c, d, a, b, x[i+ 2], 17,  606105819);
        b = this.md5_ff(b, c, d, a, x[i+ 3], 22, -1044525330);
        a = this.md5_ff(a, b, c, d, x[i+ 4], 7 , -176418897);
        d = this.md5_ff(d, a, b, c, x[i+ 5], 12,  1200080426);
        c = this.md5_ff(c, d, a, b, x[i+ 6], 17, -1473231341);
        b = this.md5_ff(b, c, d, a, x[i+ 7], 22, -45705983);
        a = this.md5_ff(a, b, c, d, x[i+ 8], 7 ,  1770035416);
        d = this.md5_ff(d, a, b, c, x[i+ 9], 12, -1958414417);
        c = this.md5_ff(c, d, a, b, x[i+10], 17, -42063);
        b = this.md5_ff(b, c, d, a, x[i+11], 22, -1990404162);
        a = this.md5_ff(a, b, c, d, x[i+12], 7 ,  1804603682);
        d = this.md5_ff(d, a, b, c, x[i+13], 12, -40341101);
        c = this.md5_ff(c, d, a, b, x[i+14], 17, -1502002290);
        b = this.md5_ff(b, c, d, a, x[i+15], 22,  1236535329);

        a = this.md5_gg(a, b, c, d, x[i+ 1], 5 , -165796510);
        d = this.md5_gg(d, a, b, c, x[i+ 6], 9 , -1069501632);
        c = this.md5_gg(c, d, a, b, x[i+11], 14,  643717713);
        b = this.md5_gg(b, c, d, a, x[i+ 0], 20, -373897302);
        a = this.md5_gg(a, b, c, d, x[i+ 5], 5 , -701558691);
        d = this.md5_gg(d, a, b, c, x[i+10], 9 ,  38016083);
        c = this.md5_gg(c, d, a, b, x[i+15], 14, -660478335);
        b = this.md5_gg(b, c, d, a, x[i+ 4], 20, -405537848);
        a = this.md5_gg(a, b, c, d, x[i+ 9], 5 ,  568446438);
        d = this.md5_gg(d, a, b, c, x[i+14], 9 , -1019803690);
        c = this.md5_gg(c, d, a, b, x[i+ 3], 14, -187363961);
        b = this.md5_gg(b, c, d, a, x[i+ 8], 20,  1163531501);
        a = this.md5_gg(a, b, c, d, x[i+13], 5 , -1444681467);
        d = this.md5_gg(d, a, b, c, x[i+ 2], 9 , -51403784);
        c = this.md5_gg(c, d, a, b, x[i+ 7], 14,  1735328473);
        b = this.md5_gg(b, c, d, a, x[i+12], 20, -1926607734);

        a = this.md5_hh(a, b, c, d, x[i+ 5], 4 , -378558);
        d = this.md5_hh(d, a, b, c, x[i+ 8], 11, -2022574463);
        c = this.md5_hh(c, d, a, b, x[i+11], 16,  1839030562);
        b = this.md5_hh(b, c, d, a, x[i+14], 23, -35309556);
        a = this.md5_hh(a, b, c, d, x[i+ 1], 4 , -1530992060);
        d = this.md5_hh(d, a, b, c, x[i+ 4], 11,  1272893353);
        c = this.md5_hh(c, d, a, b, x[i+ 7], 16, -155497632);
        b = this.md5_hh(b, c, d, a, x[i+10], 23, -1094730640);
        a = this.md5_hh(a, b, c, d, x[i+13], 4 ,  681279174);
        d = this.md5_hh(d, a, b, c, x[i+ 0], 11, -358537222);
        c = this.md5_hh(c, d, a, b, x[i+ 3], 16, -722521979);
        b = this.md5_hh(b, c, d, a, x[i+ 6], 23,  76029189);
        a = this.md5_hh(a, b, c, d, x[i+ 9], 4 , -640364487);
        d = this.md5_hh(d, a, b, c, x[i+12], 11, -421815835);
        c = this.md5_hh(c, d, a, b, x[i+15], 16,  530742520);
        b = this.md5_hh(b, c, d, a, x[i+ 2], 23, -995338651);

        a = this.md5_ii(a, b, c, d, x[i+ 0], 6 , -198630844);
        d = this.md5_ii(d, a, b, c, x[i+ 7], 10,  1126891415);
        c = this.md5_ii(c, d, a, b, x[i+14], 15, -1416354905);
        b = this.md5_ii(b, c, d, a, x[i+ 5], 21, -57434055);
        a = this.md5_ii(a, b, c, d, x[i+12], 6 ,  1700485571);
        d = this.md5_ii(d, a, b, c, x[i+ 3], 10, -1894986606);
        c = this.md5_ii(c, d, a, b, x[i+10], 15, -1051523);
        b = this.md5_ii(b, c, d, a, x[i+ 1], 21, -2054922799);
        a = this.md5_ii(a, b, c, d, x[i+ 8], 6 ,  1873313359);
        d = this.md5_ii(d, a, b, c, x[i+15], 10, -30611744);
        c = this.md5_ii(c, d, a, b, x[i+ 6], 15, -1560198380);
        b = this.md5_ii(b, c, d, a, x[i+13], 21,  1309151649);
        a = this.md5_ii(a, b, c, d, x[i+ 4], 6 , -145523070);
        d = this.md5_ii(d, a, b, c, x[i+11], 10, -1120210379);
        c = this.md5_ii(c, d, a, b, x[i+ 2], 15,  718787259);
        b = this.md5_ii(b, c, d, a, x[i+ 9], 21, -343485551);

        a = this.safe_add(a, olda);
        b = this.safe_add(b, oldb);
        c = this.safe_add(c, oldc);
        d = this.safe_add(d, oldd);
    }
    return Array(a, b, c, d);

}
HubJS.crypto.MD5.prototype.binl2hex = function(binarray)
{
    var hex_tab = this.hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
    var str = "";
    for(var i = 0; i < binarray.length * 4; i++)
    {
        str += hex_tab.charAt((binarray[i>>2] >> ((i%4)*8+4)) & 0xF) +
        hex_tab.charAt((binarray[i>>2] >> ((i%4)*8  )) & 0xF);
    }
    return str;
}

HubJS.crypto.MD5.prototype.md5_cmn = function(q, a, b, x, s, t)
{
    return this.safe_add(this.bit_rol(this.safe_add(this.safe_add(a, q), this.safe_add(x, t)), s),b);
}
HubJS.crypto.MD5.prototype.md5_ff = function(a, b, c, d, x, s, t)
{
    return this.md5_cmn((b & c) | ((~b) & d), a, b, x, s, t);
}
HubJS.crypto.MD5.prototype.md5_gg = function(a, b, c, d, x, s, t)
{
    return this.md5_cmn((b & d) | (c & (~d)), a, b, x, s, t);
}
HubJS.crypto.MD5.prototype.md5_hh = function(a, b, c, d, x, s, t)
{
    return this.md5_cmn(b ^ c ^ d, a, b, x, s, t);
}
HubJS.crypto.MD5.prototype.md5_ii = function(a, b, c, d, x, s, t)
{
    return this.md5_cmn(c ^ (b | (~d)), a, b, x, s, t);
}
HubJS.crypto.MD5.prototype.safe_add = function(x, y)
{
    var lsw = (x & 0xFFFF) + (y & 0xFFFF);
    var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
    return (msw << 16) | (lsw & 0xFFFF);
}
HubJS.crypto.MD5.prototype.bit_rol = function(num, cnt)
{
    return (num << cnt) | (num >>> (32 - cnt));
}



/**
 *
 * @class Base64
 * @example
 * var base64 = new HubJS.crypto.Base64();
 * var md5_string = base64.encode('aaaa');
 */
HubJS.namespace('HubJS.crypto.Base64');
HubJS.crypto.Base64 = function(){
    this._keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
}

HubJS.crypto.Base64.prototype.encode = function(input){
    var output = "";
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
    var i = 0;

    input = this._utf8_encode(input);

    while (i < input.length) {

        chr1 = input.charCodeAt(i++);
        chr2 = input.charCodeAt(i++);
        chr3 = input.charCodeAt(i++);

        enc1 = chr1 >> 2;
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
        enc4 = chr3 & 63;

        if (isNaN(chr2)) {
            enc3 = enc4 = 64;
        } else if (isNaN(chr3)) {
            enc4 = 64;
        }

        output = output +
        this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
        this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);

    }

    return output;
}

HubJS.crypto.Base64.prototype.decode = function(input){
    var output = "";
    var chr1, chr2, chr3;
    var enc1, enc2, enc3, enc4;
    var i = 0;

    input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

    while (i < input.length) {

        enc1 = this._keyStr.indexOf(input.charAt(i++));
        enc2 = this._keyStr.indexOf(input.charAt(i++));
        enc3 = this._keyStr.indexOf(input.charAt(i++));
        enc4 = this._keyStr.indexOf(input.charAt(i++));

        chr1 = (enc1 << 2) | (enc2 >> 4);
        chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
        chr3 = ((enc3 & 3) << 6) | enc4;

        output = output + String.fromCharCode(chr1);

        if (enc3 != 64) {
            output = output + String.fromCharCode(chr2);
        }
        if (enc4 != 64) {
            output = output + String.fromCharCode(chr3);
        }

    }
    output = this._utf8_decode(output);
    return output;
}

HubJS.crypto.Base64.prototype._utf8_encode = function(string){
    string = string.replace(/\r\n/g,"\n");
    var utftext = "";

    for (var n = 0; n < string.length; n++) {

        var c = string.charCodeAt(n);

        if (c < 128) {
            utftext += String.fromCharCode(c);
        }
        else if((c > 127) && (c < 2048)) {
            utftext += String.fromCharCode((c >> 6) | 192);
            utftext += String.fromCharCode((c & 63) | 128);
        }
        else {
            utftext += String.fromCharCode((c >> 12) | 224);
            utftext += String.fromCharCode(((c >> 6) & 63) | 128);
            utftext += String.fromCharCode((c & 63) | 128);
        }

    }

    return utftext;
}

HubJS.crypto.Base64.prototype._utf8_decode = function(utftext){
    var string = "";
    var i = 0;
    var c = c1 = c2 = 0;

    while ( i < utftext.length ) {

        c = utftext.charCodeAt(i);

        if (c < 128) {
            string += String.fromCharCode(c);
            i++;
        }
        else if((c > 191) && (c < 224)) {
            c2 = utftext.charCodeAt(i+1);
            string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
            i += 2;
        }
        else {
            c2 = utftext.charCodeAt(i+1);
            c3 = utftext.charCodeAt(i+2);
            string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
            i += 3;
        }

    }

    return string;
}



/**
 * @class AjaxHistory
 * @example
 *http://jindo.dev.naver.com/docs/jindo-mobile/archive/latest/source/jindo.m.AjaxHistory.js
 *http://jindo.dev.naver.com/docs/jindo-mobile/archive/latest/sample/latest/jindo.m.AjaxHistory/default.html
 */
HubJS.namespace('HubJS.AjaxHistory');
HubJS.AjaxHistory = function(option){
    var default_option = {
        nCheckInterval : 100
    };

    this.option = default_option;
    this.option = (option || {});

    this.callbacks = {
        load:function(){},
        change:function(data){}

    };
}

HubJS.AjaxHistory.prototype.initialize = function(){
    var that = this;
    var has = 'onpopstate' in window;
    if(has){
        window.onpopstate = function(event){
            that._onPopState(event);
        }
    }
    //console.log(this.callbacks);
    this.callbacks['load'].apply(this,[]);
    return this;
}

HubJS.AjaxHistory.prototype.destroy = function(){}

HubJS.AjaxHistory.prototype.addHistory = function(data, isInitialLoad){
    if(isInitialLoad){
        this._replaceState(data);
    }else{
        this._pushState(data);
    }
}

HubJS.AjaxHistory.prototype.attach = function(callbacks){

    if(callbacks['load']!=undefined && (typeof callbacks['load'] == 'function')){
        this.callbacks['load'] = callbacks['load'];
    }
    if(callbacks['change']!=undefined && (typeof callbacks['change'] == 'function')){
        this.callbacks['change'] = callbacks['change'];
    }
}

HubJS.AjaxHistory.prototype._onPopState = function(event){
    this.callbacks['change'].apply(this,[event.state]);
}

HubJS.AjaxHistory.prototype._replaceState = function(data){
    history.replaceState( data, document.title, location.href );
}
HubJS.AjaxHistory.prototype._pushState = function(data){
    history.pushState( data, document.title, location.href );
}


/**
 * Segmented Button Controller
 * @class SegmentedControl
 * @example
 * var doms = new Array($('#segment_1'),$('#segment_2'),$('#segment_3'));
 * var segment = HubJS.ui.SegmentedControl(doms,0,{select:function(index,dom){},unselect:function(index,dom){}});
 *
 */
//HubJS.namespace('HubJS.ui.SegmentedControl');
var HubJS = HubJS || {};
HubJS.ui = HubJS.ui || {};
HubJS.ui.SegmentedControl = function(dom_array, current_index, selected_callback){
    this._dom_array = dom_array;
    this._current_index = current_index;
    this._selected_callback = selected_callback;

    //:TODO click 대신 touch...
    var that = this;
    $.each(this._dom_array,function(i){
        $(this).bind('click',function(e){
            if(that._current_index == i)
                return;

            that._selected_callback["unselect"].apply(that._dom_array[that._current_index],new Array(that._current_index,that._dom_array[that._current_index]));
            that._current_index = i;
            that._selected_callback["select"].apply(that._dom_array[that._current_index],new Array(i,this));
        });
    });
}


/**
 * Loading : 로딩표시
 * @param
 * @class Loading
 * @example
 *  var hubObj = new hubjs.m.Loading($('#target'), {height:'100px', width:'100px'});
 *
 *  $('#show').bind('click',function(e){
 *      hubObj.show();
 *  });
 *  $('#hide').bind('click',function(e){
 *      hubObj.hide();
 *  });
 */
//HubJS.namespace('HubJS.ui.Loading');
var HubJS = HubJS || {};
HubJS.ui = HubJS.ui || {};
HubJS.ui.Loading = function(id_string,option){
    this._selector = 'body';
    if(!(id_string == undefined || id_string == null)){
        this._selector = '#'+id_string;
    }
    this._target = null;
    this._height = $(this._selector).height();
    this._width = $(this._selector).width();
    for(item in option){}
    var embeded_html = '<div style="position: relative; display: none;" class="_loading_container_class_">'
    +'<div style="position: absolute; padding: 0px; margin: 0px; border: 0px; background-color: gray; zoom: 1; opacity: 0.5; width: 100%; height: 100%; left: 0px; top: 0px; z-index: 1000; "></div>'
    +'<div style="z-index: 1000; position: absolute; top: 50%; left: 50%; margin-left: -36px; margin-top: -25px; ">'
    +'<div id="floatingBarsG">'
    +'<div class="blockG" id="rotateG_01"></div>'
    +'<div class="blockG" id="rotateG_02"></div>'
    +'<div class="blockG" id="rotateG_03"></div>'
    +'<div class="blockG" id="rotateG_04"></div>'
    +'<div class="blockG" id="rotateG_05"></div>'
    +'<div class="blockG" id="rotateG_06"></div>'
    +'<div class="blockG" id="rotateG_07"></div>'
    +'<div class="blockG" id="rotateG_08"></div>'
    +'</div>'
    +'<div style="margin: 2px 0px 0px; bottom: 0px; width: 100%; text-align: center;z-index: 2000;">Loading</div>'
    +'</div>'
    +'</div>';
    embeded_html = $(embeded_html);

    this._target = $(embeded_html);
    $(this._selector).append(embeded_html);
    $(embeded_html).css('height',this._height+'px');
    $(embeded_html).css('width', this._width+'px');
    if(this._selector == 'body'){
        $(embeded_html).css('position', 'absolute');
        $(embeded_html).css('position','absolute');
        $(embeded_html).css('top','0px');
    }
}

HubJS.ui.Loading.prototype.show = function(){
    var target = $(this._target);

    $(target).css('opacity','0.0');
    $(target).animate({
        opacity: 1.0
    }, 500, function() {
        //callback
        });
    $(this._target).css('display','block');

}

HubJS.ui.Loading.prototype.hide = function(){
    var target = $(this._target);
    $(target).css('opacity','1.0');
    $(target).animate({
        opacity: 0.0
    }, 500, function() {
        //callback
        $(target).css('display','none');
    });
}

/**
 * Pagination : 페이지 만을때 Pagenation
 * @param : 전체 아이템 개수, 한페이지당 보여줄 아이템 개수, 현재 페이지
 * @class Pagination
 * @example
 *  var itemCountTotal = 5;  //전체 아이템 개수
 *  var itemCountPerPage = 2; //한 페이지 나타낼 아이템 개수
 *  var currentPage = 0;
 *
 *  var pagination = new HubJS.Pagination(itemCountTotal, itemCountPerPage);
 *  var pageCountTotal = pagination.getPageCountTotal();
 *  pagination.setCurrentPage(currentPage);
 *
 *  console.log('전체 페이지 수 : '+pageCountTotal);
 *
 *  var start = pagination.getIndexOfStartItemWithPage(currentPage);
 *  var end = pagination.getIndexOfEndItemWithPage(currentPage);
 *
 *  var hasPrevPage = pagination.hasPrevPage();
 *  var hasNextPage = pagination.hasNextPage();
 *
 *  console.log('hasPrevPage : '+hasPrevPage);
 *  console.log('hasNextPage : '+hasNextPage);
 *
 *  console.log('item index range : '+start+'~'+end);
 *
 */
HubJS.namespace('HubJS.Pagination');
HubJS.Pagination = function(itemCountTotal, itemCountPerPage){
    this._itemCountTotal = itemCountTotal;
    this._itemCountPerPage = itemCountPerPage;
    this._currentPage = 0;
    this._setup();
}
HubJS.Pagination.prototype._setup = function(){


    }
//전체 아이템 개수 설정 1 bounded count
HubJS.Pagination.prototype.setItemCountTotal = function(itemCountTotal){
    this._itemCountTotal = itemCountTotal;
}
//한 페이지당 보여줄 아이템 개수 설정 1 bounded count
HubJS.Pagination.prototype.setItemCountPerPage = function(itemCountPerPage){
    this._itemCountPerPage = itemCountPerPage;
}
//현재 페이지를 설정한다. 0 bounded count
HubJS.Pagination.prototype.setCurrentPage = function(currentPage){
    //TODO:exception or return boolean currentPage가 최소 최대 범위에 들어가지 않을때
    this._currentPage = currentPage;
}
//전체 아이템 개수 설정 1 bounded count
HubJS.Pagination.prototype.getItemCountTotal = function(){
    return this._itemCountTotal;
}
//한 페이지당 보여줄 아이템 개수 설정 1 bounded count
HubJS.Pagination.prototype.getItemCountPerPage = function(){
    return this._itemCountPerPage;
}
//현재 페이지를 설정한다. 0 bounded count
HubJS.Pagination.prototype.getCurrentPage = function(){
    return this._currentPage;
}
/**
 * @return boolean
 */
HubJS.Pagination.prototype.hasPrevPage = function(){
    if(this._currentPage == 0)
        return false;
    return true;
}
/**
 * @return boolean
 */
HubJS.Pagination.prototype.hasNextPage = function(){
    var currentPage = this._currentPage+1; // 0 bounded to 1 bounded
    var _numberOfPage = (this._itemCountTotal)/(this._itemCountPerPage);
    _numberOfPage = Math.ceil(_numberOfPage);
    if(currentPage >= _numberOfPage)
        return false;
    else
        return true;
}

//전체 페이지 개수 1 bounded count
HubJS.Pagination.prototype.getPageCountTotal = function(){
    var _numberOfPage = (this._itemCountTotal)/(this._itemCountPerPage);
    _numberOfPage = Math.ceil(_numberOfPage);
    return _numberOfPage;
}

//0 bounded count
HubJS.Pagination.prototype.getIndexOfStartItemWithPage = function(page){
    var start = this._itemCountPerPage*page;
    if(start < 0 || this._itemCountTotal < start)
        return null;
    return start;
}
//0 bounded count
HubJS.Pagination.prototype.getIndexOfEndItemWithPage = function(page){
    var start = this._itemCountPerPage*page;
    var end = this._itemCountPerPage*page+this._itemCountPerPage-1;

    if((this._itemCountTotal-1) < end && end < this._itemCountTotal+this._itemCountPerPage-1)
        return (this._itemCountTotal-1);
    else if(this._itemCountTotal+this._itemCountPerPage-1 <= end){
        return null;
    }
    return end;
}

/**
 * Validation email, password, hubid, tel, HTML, URL, IP
 * @class Validation
 * @example
 * var validation = new HubJS.Validation();
 * var ret = validation.validate('email','pomtech@com2us.com');
 * http://www.appelsiini.net/projects/lazyload
 * http://www.appelsiini.net/2007/6/sequentially-preloading-images
 * http://yuilibrary.com/yui/docs/imageloader/
 // 이벤트 등록
function setup(event) {
   var evtObject = document.getElementById("objectId");

   if (evtObject.addEventListener) {
      evtObject.addEventListener("click", handler, false);
   } else if (evtObject.attachEvent) {
      evtObject.attachEvent("onclick", handler);
   } else if (evtObject.onclick) {
      evtObject.onclick = handler;
   }
}

// 이벤트 핸들러
function handler(event) {
   // 이벤트 처리 코드
}

<img id="hubjs_image_id_1" src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw%3D%3D"/>

목적은 이미지로더 오브젝트 만들고 한번에 load 시키는 거임 여기에 이미지 리퀘스트를 큐잉으로 하면 더 발전발전
 */
HubJS.namespace('HubJS.ImageLoader');

HubJS.ImageLoader = function(options){
    this._blankImage = 'data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw%3D%3D';
    this._options = options || {};
    this._imageTable = new Array();
}
HubJS.ImageLoader.prototype._getImageTable = function(){
    return this._imageTable;
}

HubJS.ImageLoader.prototype.registerImage = function(domId, imageURL, callback){
    var imageTable = this._getImageTable();
    var callback = callback || function(){};
    imageTable[domId] = {
        'imageURL' : imageURL,
        'callback' : callback
    };
    return this;
}

HubJS.ImageLoader.prototype.load = function(){
    for(var item in this._imageTable){
        var obj = document.getElementById(item);
        //$('#'+item).bind('load',function(){alert("load");});
        obj.setAttribute("src",this._imageTable[item]['imageURL']);
        var imageloaderItem = this._imageTable[item];
        imageloaderItem['callback'].apply(this,[imageloaderItem]);
    //$('#'+item).attr('src',this._imageTable[item]);
    }
//TODO: destory all of event?.......
}

/**
 * Native
 * @class Native
 * @example
 * var native = new HubJS.Native();
 *
 */
HubJS.namespace('HubJS.Native');

HubJS.Native = function(){
    if(window['native'] == undefined){
        window['native'] = {};
    }
}

HubJS.Native.callNativeScheme = function(scheme, iframe_name){
    var target = scheme;
    if (iframe_name === null || iframe_name === undefined) {
        iframe_name = 'hub_iframe';
    }
    var iframe = $('#'+iframe_name);
    if(iframe.length === 0){
        iframe = $('<iframe id="'+iframe_name+'" style="display:none;"/>');
        $('body').append(iframe);
    }
    $(iframe).attr('src',target);
}

/**
 * @param type 'camera' or 'gallery'
 * callback to window.native.getPictureCallback('base64');
 */
HubJS.Native.prototype.getPicture = function(type){
    var target;
    if(type=="camera"){
        target = "c2shub://getpicture?type=camera";
        //window.location.href = target;
    }else{
        target = "c2shub://getpicture?type=gallery";
        //window.location.href = target;
    }
    HubJS.Native.callNativeScheme(target);
}

/**
 * @param type 'phonenumber' or 'email'
 * callback to window.native.getAddressBookCallback('phonenumber');
 */
HubJS.Native.prototype.getAddressBook = function(type,all){
    if(all==undefined || all == false)
        all='false';
    else
        all='true';

    var target;
    if(type=="phonenumber"){
        target = "c2shub://getaddressbook?type=phonenumber&all="+all;
        //window.location.href = target;
    }else{
        target = "c2shub://getaddressbook?type=email&all=";
        //window.location.href = target;
    }
    HubJS.Native.callNativeScheme(target);
}

/**
 * 201510 
 * callback to window.native.getAndroidMPhoneCallback();
 */
HubJS.Native.prototype.getAndroidMPhoneCallappsettings = function(){
    var target = "c2shub://callappsettings";
    HubJS.Native.callNativeScheme(target);
}


/**
 * callback to window.native.getPhoneNumberCallback('phonenumber');
 */
HubJS.Native.prototype.getPhoneNumber = function(){
    var target = "c2shub://getphonenumber";
    HubJS.Native.callNativeScheme(target);
    //window.location.href = target;
}


HubJS.namespace('HubJS.Native.Android');

HubJS.Native.Android = function() {
    if(window['native'] === undefined){
        window['native'] = {};
    }
	window['native'].goBack = function(){
		console.log("goBack");
		return true;
    }

}




/**
 * Native
 * @class Native
 * @example
 * var native = new HubJS.Native();
 *
 *https://developers.facebook.com/docs/reference/javascript/FB.login/
 */
HubJS.namespace('HubJS.Native.FB');

HubJS.Native.FB = function(){
    if(window['native'] === undefined){
        window['native'] = {};
    }

    this.appId='';
    this.loginResponse = null;
    this.accessToken = null;
    this.baseURL = 'https://graph.facebook.com';

    var that = this;
    window['native'].getFacebookAccessTokenCallback = function(accessToken){
        if (!accessToken) {
            accessToken = null;
        }
        that.loginCallback(accessToken);
    }
}
HubJS.Native.FB.prototype.getBaseURL = function(){
    return this.baseURL;
}
HubJS.Native.FB.prototype.setAccessToken = function(accessToken){
    this.accessToken = accessToken;
}
HubJS.Native.FB.prototype.getAccessToken = function(){
    return this.accessToken;
}

HubJS.Native.FB.prototype.loginCallback = function(accessToken){
    if(this.loginResponse != null){
        this.setAccessToken(accessToken);
        this.loginResponse.apply(this,[accessToken]);
    }
//this.initialize.apply(this, arguments);
}
/**
 * var fb = new HubJS.Native.FB();
 * fb.init('324k324l2');
 */
HubJS.Native.FB.prototype.init = function(appId){
    this.appId = appId;

}
/**
 * var fb = new HubJS.Native.FB();
 * fb.init('324k324l2');
 * fb.login(function(token){
 *
 * });
 */
HubJS.Native.FB.prototype.login = function(loginResponse, option){
    //1.facebook/get_access_token 에 ajax 접근해 token을 가져와 본다. ajax에서는 유효 token 검증까지

    //1-1 token 유

    //1-2 token 무

    //1-2-1 ios 접근

    //1-2-1-1 ios token 가져오기 성공

    //1-2-1-2 ios token 가져오기 성공하지 못하면 web이다 web facebook token 가져오기 실행

    //1-2-1-(1,2)-1 facebook/set_access_token 에 ajax 접근해 token을 설정한다. callback 을 호출한다.
    this.loginResponse = loginResponse;
    var appId = this.appId;

    var that = this;

    //1-2-1 ios 접근
    /*
    var iframe = $('#hub_iframe');
    if(iframe.length === 0){
        iframe = $('<iframe id="hub_iframe" style="display:none;"/>');
        $('body').append(iframe);
    }
    */
    if (option === undefined) {
        option = {};
    }
    if (option.scope === undefined) {
        option.scope = "email";
    }

    if (option.type === undefined) {
        option.type = "read";
    }

    var target = "c2shub://facebook/get_token?client_id="+appId+"&type="+option.type+"&scope="+option.scope;
    HubJS.Native.callNativeScheme(target);
    //$(iframe).attr('src',target);
}
/**
 * var fb = new HubJS.Native.FB();
 * fb.init('324k324l2');
 * fb.api('/me', function(response) {
 *
 * });
 */
HubJS.Native.FB.prototype.api = function(path, responseCallback){
    var accessToken = this.getAccessToken();
    var requestURL = this.getBaseURL()+path+'&access_token='+accessToken;
    $.getJSON(requestURL+'&callback=?', function(data){
        responseCallback.apply(this,[data]);
    });
}

HubJS.Native.FB.prototype.apprequests = function(params){
    var serialized = function(params) {
            var stripped = [];
            for ( var k in params) {
                stripped.push(k + "=" + encodeURIComponent(params[k]));
            }
            return stripped.join("&");
    }
    var json_str = serialized(params);
    var target = "c2shub://facebook/apprequests?"+json_str;
    HubJS.Native.callNativeScheme(target);
    //location.href = "c2shub://facebook/apprequests?"+json_str;
}

HubJS.namespace('HubJS.Native.SocialNetwork');
HubJS.Native.SocialNetwork = function(serviceType) {
    this.serviceType = null;
    if(window['native'] === undefined){
        window['native'] = {};
    }
    switch(serviceType) {
        case 'sinaweibo':
        case 'googleplus' :
        case 'facebook':
            this.serviceType = serviceType;
            break;
        default:
            return false;
    }
    this.getSocialUserDataCallback = null;
    this.getSocialUserTokenCallback = null;
    this.socialLogoutResultCallback = null;
	this.socialIsAuthorizedResultCallback = null;
    var that = this;

    window['native'].putSocialUserData = function(user_data){
        if (!user_data) {
            user_data = null;
        }
        that.getSocialUserDataCallback(user_data);
    };
    window['native'].putSocialFriendList = function(friends_list) {
        if (!friends_list.friends) {
            friends_list.friends = [];
        }
        that.getSocialFriendsListCallback(friends_list);
    };
	window['native'].putSocialUserToken = function(user_data){
        if (!user_data) {
            user_data = null;
        }
        that.getSocialUserTokenCallback(user_data);
    };
	window['native'].socialLogoutResultCallback = function(user_data){
        if (!user_data) {
            user_data = null;
        }
        that.socialLogoutResultCallback(user_data);
    };
	window['native'].socialIsAuthorizedResult = function(user_data) {
		if (!user_data) {
            user_data = null;
        }
        that.socialIsAuthorizedResult(user_data);
	}
};

HubJS.Native.SocialNetwork.prototype.getUserData = function(callback) {
    this.getSocialUserDataCallback = callback;
    if (!this.serviceType) {
        return false;
    }
    var url = "c2shub://social/request_user_profile?service=" + this.serviceType;
    //var url = '/test/social_get_user_test';
    HubJS.Native.callNativeScheme(url);
};

HubJS.Native.SocialNetwork.prototype.getUserToken = function(callback) {
    this.getSocialUserTokenCallback = callback;
    if (!this.serviceType) {
        return false;
    }
    var url = "c2shub://social/request_user_token?service=" + this.serviceType;
    //var url = '/test/social_get_user_test';
    HubJS.Native.callNativeScheme(url);
};

HubJS.Native.SocialNetwork.prototype.getFriendsList = function(callback) {
    this.getSocialFriendsListCallback = callback;
    if (!this.serviceType) {
        return false;
    }
    var url = "c2shub://social/request_friends?service=" + this.serviceType;
    //var url = '/test/social_get_friend_test';
    HubJS.Native.callNativeScheme(url);
};

HubJS.Native.SocialNetwork.prototype.logout = function(callback) {
    this.socialLogoutResultCallback = callback;
    if (!this.serviceType) {
        return false;
    }
    var url = "c2shub://social/logout?service=" + this.serviceType;
    //var url = '/test/social_get_friend_test';
    HubJS.Native.callNativeScheme(url);
};


/**
 * @class Toast
 * @example
 * HubJS.ui.Toast.show("message");
 */
var HubJS = HubJS || {};
HubJS.ui = HubJS.ui || {};
HubJS.ui.Toast = function(){
    this._id = "hubjs_toast";
    this._timer = null;
    this._delay = 3000;
}

HubJS.ui.Toast.prototype.show = function(text){
    if(this._timer != null){
        $('#'+this._id).css("opacity","0.0");
        clearInterval(this._timer);
    }
    var el = $('#'+this._id);
    if(el.length == 0){
        var toast_html = '<p id="'+this._id+'" style="position:absolute;top:50px;margin:0;color:#fff;font-size:14px;font-weight:bold;text-align:center;border:2px solid #fff;border-radius:8px;-webkit-border-radius:8px;background-color:#333;box-shadow:2px 2px 5px rgba(0,0,0,0.7),-2px -2px 5px rgba(0,0,0,0.7);-webkit-box-shadow:2px 2px 5px rgba(0,0,0,0.7),-2px -2px 5px rgba(0,0,0,0.7);opacity: .9;-webkit-transition: opacity 0.5s ease-out;-moz-transition: opacity 0.5s ease-out;-ms-transition: opacity 0.5s ease-out;-o-transition: opacity 0.5s ease-out;transition: opacity 0.5s ease-out;z-index:1000;">'+text+'</p>';
        $('body').append(toast_html);
    }else{
        $('#'+this._id).text(text);
    }

    var top = ( $(window).scrollTop() + ($(window).height() - $('#'+this._id).height()) / 2 );
    var margin_left = -1*($('#'+this._id).width()/2);

    var getWidth = function ()
    {
        xWidth = null;
        if(window.screen != null)
            xWidth = window.screen.availWidth;

        if(window.innerWidth != null)
            xWidth = window.innerWidth;

        if(document.body != null)
            xWidth = document.body.clientWidth;

        return xWidth;
    }


    $('#'+this._id).css("opacity","0.9");

    $('#'+this._id).css({
        'padding-left':'10px'
        ,'padding-right':'10px'
        ,'padding-top':'7px'
        ,'padding-bottom':'7px'
    }).css({
        'top':top
        ,
        'left':(getWidth()/2-$('#'+this._id).outerWidth()/2)

    });

    var that = this;
    this._timer = setInterval(function(){
        $('#'+that._id).css("opacity","0.0");
        clearInterval(that._timer);
        that._timer = null;
        $('#'+that._id).remove();
    }, that._delay);

}

/**
 * @class AjaxHistory
 * @example
 * <input id="id_of_text" type="text" value="text" data-placeholer=""/>
 *  var textInput = new HubJS.ui.TextInput('id_of_text',{});
 */
var HubJS = HubJS || {};
HubJS.ui = HubJS.ui || {};
HubJS.ui.TextInput = function(id_string, options){
    this.id_string = id_string;
    this.placeHolder = "";
    this.isPassword = false;

    for (var item in options) {}
    var el = $('#'+this.id_string);
    if($(el).attr('type') == 'password'){
        this.isPassword = true;
    }

    var placeHolder = $(el).attr('data-placeholer');
    if(placeHolder == undefined) placeHolder = "";
    this.placeHolder = placeHolder;

    if($(el).val()==''){
        $(el).val(this.placeHolder);

        if(this.isPassword){
            var element = $(el);
            element[0].type ="text";
        }
    }

    var that = this;

    if(!this.isPassword){
        $(el).bind('focus',function(e){
            if($(el).val()==that.placeHolder){
                $(el).val('');
            }
        }).bind('blur',function(e){
            if($(el).val()==''){
                $(el).val(that.placeHolder);
            }
        });
    }else{
        $(el).bind('focus',function(e){
            if($(el).val()==that.placeHolder){
                $(el).val('');
                var element = $(el);
                element[0].type ="password";
            }else{
                var element = $(el);
                element[0].type ="password";
            }
        }).bind('blur',function(e){
            if($(el).val()==''){
                $(el).val(that.placeHolder);
                var element = $(el);
                element[0].type ="text";
            }else{
                var element = $(el);
                element[0].type ="password";
            }
        });
    }
}
HubJS.ui.TextInput.prototype.getPlaceHolderString = function(){
    return this.placeHolder;
}

HubJS.ui.TextInput.prototype.getValue = function(){
    var el = $('#'+this.id_string);
    var value = $(el).val();
    if(value == this.getPlaceHolderString()){
        return "";
    }
    return value;
}


/**
 * Dialog for hub2
 * @class Dialog
 * @example
 * var validation = new HubJS.Dialog();
 * var ret = validation.validate('email','pomtech@com2us.com');
 * http://www.appelsiini.net/projects/lazyload
 * http://www.appelsiini.net/2007/6/sequentially-preloading-images
 * http://yuilibrary.com/yui/docs/imageloader/
 */
//HubJS.namespace('HubJS.ui.Dialog');
var HubJS = HubJS || {};
HubJS.ui = HubJS.ui || {};
HubJS.ui.Dialog = function(layer_id_string, dialog_id_string){
    this.layer_id_string = layer_id_string;
    this.dialog_id_string = dialog_id_string;

    var el_layer = document.getElementById(this.layer_id_string);
    if(el_layer == null)
        return;
    el_layer.style.display = 'none';

    var that = this;
    var hasOrientation = "onorientationchange" in window;
    var orientationEvent = hasOrientation ? "orientationchange" : "resize";
    var windowListenerFired = false;
    var documentListenerFired = false;
    $(window).bind(orientationEvent, function(e){
        if (documentListenerFired) {
            return true;
        }
        that._setPosition();
        windowListenerFired = true;
    });
    $(document).bind(orientationEvent, function(e){
        if (windowListenerFired) {
            return true;
        }
        that._setPosition();
        documentListenerFired = true;
    });
}
HubJS.ui.Dialog.prototype.hide = function(){
    var el_layer = document.getElementById(this.layer_id_string);
    el_layer.style.display = "none";
    var el_dialog = document.getElementById(this.dialog_id_string);
    el_dialog.style.display = "none";
}

HubJS.ui.Dialog.prototype.show = function(){
    var el_layer = document.getElementById(this.layer_id_string);
    el_layer.style.display = "block";
    $(el_layer).children().each(function(i,item){
        $(item).css('display','none');
    });
    var el_dialog = document.getElementById(this.dialog_id_string);
    el_dialog.style.display = "block";


    this._setPosition();
}

HubJS.ui.Dialog.prototype._setPosition = function(){
    var el_layer = document.getElementById(this.layer_id_string);
    var el_dialog = document.getElementById(this.dialog_id_string);
    $(el_layer).css({
        'height':$(document).height(),
        'width':$(window).width()
    });
    var top = ( $(window).scrollTop() + ($(window).height() - $(el_dialog).height()) / 2 );
	
	$(el_dialog).css({
        'top':top
    });
}


/**
 * @class ImageViewer
 * @example
 *
 * var imageViewer = new HubJS.ui.ImageViewer();
 * imageViewer.show('http://imageurl');
 * imageviewer.hide();
 *
 */
var HubJS = HubJS || {};
HubJS.ui = HubJS.ui || {};

// ListMore
// 2015.06.26. frizzle
//HubJS.ui.ListMore = function(ul, btn_view_more, length, url, ui_generator, after_create_li) {
HubJS.ui.ListMore = function(data) {

	this._ul = data.ul;
	this._btn_view_more = data.btn_view_more;
	this._url = data.url;
	this._ui_generator = data.ui_generator;
	this._page = 1;
	this._length = data.length;
	this._after_create_li = data.after_create_li;
	this._nothing_msg = data.nothing_msg;
	this._show_exist= data.show_exist;
	this.size = 0;


	var that = this;
	if(this._nothing_msg !== undefined) {
		this._nothing_msg.hide();
		this._ul.show();
	}
	if(this._show_exist !== undefined) {
		this._show_exist.hide();
	}

	this._btn_view_more.click(function() {
		$(this).hide();
		$.ajax({
			type : "post",
			cache : false,
			data : {
				page : that._page,
				length : that._length,
			},
			url : that._url + "?d=" + new Date().getTime(),
			success : function(data, textStatus, jqXHR) {
				data = $.parseJSON(data);

				that._page ++;
				if(data.length >= that._length) {
					that._btn_view_more.show();
				}
				for(var i = 0 ; i < data.length ; i++){
					that._ul.append(that._ui_generator(data[i]));
					that.size++;
				}
				if(that._after_create_li !== undefined)
					that._after_create_li();
				that.Refresh();
				
			},
			error : function(jqXHR, textStatus, errorThrown){

			}
		});
	});
	this._btn_view_more.click();
};
HubJS.ui.ListMore.prototype.Refresh = function() {
	this.size = this._ul.children().length;
	if(this._nothing_msg !== undefined) {
		if(this.size > 0) {
			this._nothing_msg.hide();
			this._ul.show();
		}
		else {
			this._nothing_msg.show();
			this._ul.hide();
		}
	}
	if(this._show_exist !== undefined) {
		if(this.size > 0) {
			this._show_exist.show();
		}
		else {
			this._show_exist.hide();
		}
	}
}

// Popup
// 2015.06.29. frizzle
HubJS.ui.Popup = function(popup_name) {
	this._popup = $(".popup[data-name=" + popup_name + "]");
	var that = this;
    this._popup.find(".btn_close_logout").click(function() {
        that.hide_logout();
    });
	this._popup.find(".btn_close:not(.btn_close_logout), .btn_cancel, .btn_close_qr").click(function() {
		that.hide();
	});
};
HubJS.ui.Popup.prototype.bind = function( e, selector, handle ) {
	this._popup.find(selector).bind(e, handle);
};
HubJS.ui.Popup.prototype.find = function(selector) {
	return this._popup.find(selector);
};
HubJS.ui.Popup.prototype.show = function() {
	this._popup.show();
	$("html").addClass("pop_scroll");
};
HubJS.ui.Popup.prototype.hide = function() {
	this._popup.hide();
    $("html").removeClass("pop_scroll");
};
HubJS.ui.Popup.prototype.hide_logout = function() {
    this._popup.hide();
};

// Form Helper
// 2015.08.10. frizzle
HubJS.ui.FormHelper = function() {
		
};
HubJS.ui.FormHelper.prototype.LimitTextLength = function(input, limitLength, limitDelegate) {
	input.bind('keyup input paste', function() {
		var value = $(this).val();
		if(value.length > limitLength) {
			$(this).val(value.substring(0, limitLength));
			if(limitDelegate !== undefined) {
				limitDelegate();	
			}
		}
	});
};
HubJS.ui.FormHelper.prototype.ShowTextLength = function(input, show) {
	input.bind("keyup input paste change", function() {
		var length = $(this).val().length;
		show.text(length);
	});
}
HubJS.ui.FormHelper.prototype.SetDeleteButton = function(input, deleteButton) {
	deleteButton.click(function() {
		input.val("");
	});
}
HubJS.ui.CheckBox = function(id, change) {
	this.label = $("label[for='"+id+"']");
	this.input = $("#" + id);
	this.change = change;
	var that = this;
	this.input.change(function() {
		if( $(this).is(':checked') ) {
			that.label.addClass("checked");
			that.change(true);
		}
		else {
			that.label.removeClass("checked");
			that.change(false);
		}
	});
	if(this.IsChecked())
		this.label.addClass("checked");
	else 
		this.label.removeClass("checked");

}
HubJS.ui.CheckBox.prototype.IsChecked = function() {
	return this.input.is(":checked");	
}
HubJS.ui.CheckBox.prototype.Check = function(check, enableCallback) {
	if(check) {
		this.input.prop('checked', "checked");
		this.label.addClass("checked");
	}
	else {
		this.input.prop('checked', false);
		this.label.removeClass("checked");
	}
	if(enableCallback == undefined || enableCallback == true) {
		this.change(check);
	}
}

HubJS.ui.Radio = function(radios, change) {
	var that = this;
	this.radios = radios;
	this.change = change;
	this.radios.change(function() {
		if( $(this).is(':checked') ) {
			var index;
			for(var i = 0; i < that.radios.length; i++) {
				console.log(this);
				console.log(that.radios.eq(i));
				if(this == that.radios[i]) {
					index = i;	
					break;
				}
			}
			that.Select(index);
			that.change($(this));
		}
	});
}
HubJS.ui.Radio.prototype.GetSelected = function() {
	var selected;
	this.radios.each(function() {
		if( $(this).is(":checked") ) {
			selected = this;
		}
	});
	return $(selected);
}
HubJS.ui.Radio.prototype.Select = function(index, enableCallback) {
	for(var i = 0; i < this.radios.length; i++) {
		var r = this.radios.eq(i);
		var label = r.parent().find("label[for='"+r.attr("id")+"']");

		if(index == i) {
			r.prop("checked", "checked");
			label.addClass("checked");
		}
		else {
			r.prop("checked", false);
			label.removeClass("checked");
		}
	}
}

HubJS.ui.Flicker = function(data) {
	this.view = data.view;
	this.selectCallback = data.selectCallback;
	
	var event = {};
	event.start = "touchstart";
	event.move= "touchmove";
	event.end = "touchend";

	var previousX;
	var previousY;
	var lastDx = 0;
	var isDraggng;
	var isHorizontalDrag;

	this.GetLayout();
	this.frame.css("overflow", "hidden");
	this.frame.css("position", "relative");
	this.view.css("position", "absolute");
	this.view.css("top", 0);
	this.view.css("left", 0);

	var that = this;

	this.view.bind(event.start + " " + event.move + " " + event.end, function(e) {
		switch(e.type) {
			case event.start :
				var x = e.originalEvent.touches[0].screenX;
				var y = e.originalEvent.touches[0].screenY;
				previousX = x;
				previousY = y;
				isDragging = true;
				isHorizontalDrag = 0;
				break;
			case event.move :
				if(isDragging) {
					var x = e.originalEvent.touches[0].screenX;
					var y = e.originalEvent.touches[0].screenY;
					var dx = x - previousX;
					var dy = y - previousY;
					previousX = x;
					previousY = y;
					if(isHorizontalDrag == 0) {
						_dx = dx;
						_dy = dy;

						if(_dx < 0) _dx = -_dx;
						if(_dy < 0) _dy = -_dy;

						isHorizontalDrag = _dx > _dy ? 1 : 2;

					}
					if(isHorizontalDrag == 1) {
						that.Move(dx);
						lastDx = dx;
						return false;
					}
					else {
						isDragging = false;
					}
				}
				break;
			case event.end :
				if(isDragging && isHorizontalDrag == 1) {
					var left = parseInt($(this).css("left"));
					var destination = left + lastDx * 4;
					if(that.min > destination) 
						destination = that.min;
					if(that.max < destination)
						destination = that.max;
					$(this).animate(
						{left : destination + "px"}, 
						100, 
						"linear", 
						function() {
							that.ReturnPosition();
						}
					);	
					Dragging = false;
					return false;
				}
				else {
					return true;
				}
				break;
		}
	});
}
HubJS.ui.Flicker.prototype.ReturnPosition = function() {
	var left = parseInt(this.view.css("left"));
	var destination;
	var index;

	if(this.width - this.frameWidth + left < this.contentWidth / 2) {
		destination = -(this.width - this.frameWidth);
		index = this.contentNum - 1;
	}
	else {
		index = parseInt(
			( -left+((this.contentWidth+this.contentMargin)/2) ) 
			/ (this.contentWidth+this.contentMargin)
		);
		destination = - index * (this.contentWidth+this.contentMargin);
	}
	this.view.animate({left : destination + "px"});
	if(this.selectCallback !== undefined) {
		this.selectCallback(index);
	}
}
HubJS.ui.Flicker.prototype.GetLayout = function() {
	this.frame = this.view.parent();
	this.frameWidth = parseInt(this.frame.css("width"));
	this.width = parseInt(this.view.css("width"));;	
	this.min = this.frameWidth - this.width;
	this.max = 0;
	this.contentWidth = this.view.children().last().width();
	this.contentNum = this.view.children().length;
	this.contentMargin = parseInt(this.view.children().last().css("marginLeft"));
}
HubJS.ui.Flicker.prototype.Move = function(dx) {
	var left = parseInt(this.view.css("left"));
	var destination = left + dx;
	if(this.min > destination) 
		destination = this.min;
	if(this.max < destination)
		destination = this.max;
	this.view.css("left", destination);	
}
HubJS.ui.Notification = function() {
	this.prepared = false;
	this.contentView = $(".HIVEcontents").first();
	var that = this;
	$(".pmt_header_notification .btn_close").click(function() {
		that.ShowNotification(false);
		// x버튼 클릭시 new 배찌 갱신 적용
		that.CheckNotification();
	});
	$(".pmt_header_content .btn_notice").click(function() {
		that.ShowNotification(true);
	});
	$(".all_menu_list .pmt_btn_notice").click(function() {
		that.ShowNotification(true);
		return false;
	});
	this.GetNotificationView();
	this.CheckNotification();
}
HubJS.ui.Notification.prototype.CheckNotification = function() {
	$.ajax({
		url : "/notification/ajax_get_notifications_count",
		type : "post",
		cache : false,
		success : function(data) {
			console.log(data);
			count = $.parseJSON(data);	
			console.log(count);
			
			
			
			if(count.Total > 0) {
				//NEW 한번만
				if($("#pmt_notification_button").hasClass("new")==false){
					
					$("#pmt_notification_button").addClass("new");
					$(".pmt_btn_notice").append("<em class='new'>new</em>");
					if(count.Inquiry > 0) {
						$(".pmt_notification_inquiry").append("<em class='new'>new</em>");
					}
					
				}
			
			} else {
				// x버튼 클릭시 new 배찌 갱신 적용
				if ($("#pmt_notification_button").hasClass("new")) {
					$("#pmt_notification_button").removeClass("new");
				}
				$(".pmt_btn_notice > em").remove();
				$(".pmt_notification_inquiry > em").remove();
			}
			
			if(count.Message > 0) {
				if ( $("#pmt_top_menu_message") ) {
					$("#pmt_top_menu_message").addClass("new");
				}
			} else {
				// x버튼 클릭시 new 배찌 갱신 적용
				if ($("#pmt_top_menu_message").hasClass("new")) {
					$("#pmt_top_menu_message").removeClass("new");
				}
			}
			
			
			
			console.log(data);
		},
		error : function() {
		},
	});
}
HubJS.ui.Notification.prototype.ShowNotification = function(show) {
	if(show) {
		this.contentView.hide();
		$("#pmt_notification_view").show();
		$(".pmt_header_notification").show();
		$(".pmt_header_content").hide();
		this.PrepareList();
	}
	else {
		this.contentView.show();
		$("#pmt_notification_view").hide();
		$(".pmt_header_notification").hide();
		$(".pmt_header_content").show();
	}
}
HubJS.ui.Notification.prototype.GetNotificationView = function() {
	var that = this;
	$.ajax({
		url : "/notification/ajax_get_html",
		type : "post",
		cache : false,
		success : function(data) {
			$("#HIVEcontainer").append(data);
		},
		error : function() {
		},
	});
//	$.ajax({
//		url : "/notification/ajax_get_notifications",
//		success : function(data) {
//		},
//		error : function() {
//		},
//	});
}
HubJS.ui.Notification.prototype.PrepareList = function () {
	if(this.prepared) {
		return;
	}
	this.prepared = true;
	var noti = this;
	this.ListMore = new HubJS.ui.ListMore({
		ul : $("#pmt_notification_view .notice_box"),
		btn_view_more : $("#pmt_notification_view .btn_view_more"),
		btn_view_more_layout : $("#pmt_notification_view .btn_area_b"),
		nothing_msg : $("#pmt_notification_view .error_tit, #pmt_notification_view .error_txt"),
		show_exist : $("#pmt_notification_view .select_area"),
		length : 20,
		url : "/notification/ajax_get_notifications",
		ui_generator : function(data) {
			return data;
		},
		after_create_li : function() {
			$("#pmt_notification_view .btn_decline").click(function() {
				var url = "/profile/ajax_friends/decline/" + $(this).data("uid");
				var toast = new HubJS.ui.Toast;
				var msg = $(this).data("msg");
				var error_msg = $(this).data("error_msg");
				var that = this;
				$.ajax(url, {
					'type' : 'GET',
					'success' : function(data){
						toast.show(msg);
						$(that).parents("li").remove();
						noti.ListMore.Refresh();
						return false;
					},
					"error" : function(xhr){
						if(xhr.responseText != '') {
							toast.show(xhr.responseText);
						}
						else {
							toast.show(error_msg);
						}
						return false;
					}
				});
				return false;
			});
			$('#pmt_notification_view .btn_accept').click(function(){
				var url = "/profile/ajax_friends/accept/" + $(this).data("uid");
				var toast = new HubJS.ui.Toast;
				var that = this;
				var msg = $(this).data("msg");
				var error_msg = $(this).data("error_msg");
				$.ajax(url, {
					'type' : 'GET',
					'success' : function(data){
						toast.show(msg);
						
						$(that).parents("li").remove();
						noti.ListMore.Refresh();
						return false;
					},
					"error" : function(xhr){
						if(xhr.responseText != '') {
							toast.show(xhr.responseText);
						}
						else {
							toast.show(error_msg);
						}
						return false;
					}
				});
				return false;
			});
			$(".pmt_time_string").each(function() {
				var time_stamp = $(this).data("time_stamp");
				var added = $(this).data("time_stamp_added"); if(time_stamp !== undefined && !added) {
					var realTime = new HubJS.RealTime();
					var timeString = '';
					timeString = realTime.getRealTime(
										parseInt(time_stamp)*1000, 
										'<?=get_browser_language_3_code_string();?>'
									);
					$(this).append(timeString);
					var added = $(this).data("time_stamp_added", true);
				}
			});
		},
	});
}




//HubJS.namespace('HubJS.ui.ImageViewer');
HubJS.ui.ImageViewer = function(){
    this._id_layer = 'C2Slayer';
    this._id_image = 'hubjs_image_viewer';

    if($('#'+this._id_layer).length==0){
        $('body').append('<div id="'+this._id_layer+'" style="display:none;width: 100%;height: 100%;position: absolute;top: 0;left: 0;z-index: 110;overflow: auto;background-color: rgba(0, 0, 0, 0.8);"></div>');
    }

    if($('#'+this._id_image).length == 0){
        $('#'+this._id_layer).append('<div id="'+this._id_image+'" style="display:none;text-align:center;position:relative;"><img src="" alt="" style="height:200px;width:200px;"></div>');
    }

    var that = this;

    if ('ontouchstart' in window) {
        $('#'+this._id_image+' img').bind('touchstart',function(e){
            setTimeout(function(){that.hide();}, 500);
            return false;
        });
    }
    else {
        $('#'+this._id_image+' img').bind('click',function(e){
            that.hide();
            return false;
        });
    }

    var hasOrientation = "onorientationchange" in window;
    var orientationEvent = hasOrientation ? "orientationchange" : "resize";
    $(window).bind(orientationEvent, function(e){

        that._setPosition();
    });

}

HubJS.ui.ImageViewer.prototype.show = function(image_url_string){
    var image_dom = $('#'+this._id_image).find('img');

    var that = this;
    $(image_dom).attr('src',image_url_string).load(function() {
        //var imageObj = this;
        //that._setPosition(imageObj);
    });
    //that._setPosition(image_dom);
    $('#'+this._id_layer).children().each(function(i,item){
        $(item).css('display','none');
    });

    that._setPosition(image_dom);

    $('#'+this._id_layer).css('display','block');
    $('#'+this._id_image).css('display','block');
}

HubJS.ui.ImageViewer.prototype.hide = function(){
    $('#'+this._id_layer).css('display','none');
    $('#'+this._id_image).css('display','none');
};

HubJS.ui.ImageViewer.prototype._setPosition = function(){
    /*
    var padding = 10;

    var screenHeight = this._getScreenHeight();
    var screenWidth = this._getScreenWidth();

    var width = (imageDom.naturalWidth==undefined)? imageDom.width : imageDom.naturalWidth;
    var height = (imageDom.naturalHeight==undefined)? imageDom.height : imageDom.naturalHeight;

    if(screenHeight > screenWidth){
        //portrait
        if(width > height){
            $(imageDom).width(screenWidth);
        }else{
            $(imageDom).height(screenHeight);
        }
    }else{
        //landscape
        if(width > height){
            $(imageDom).width(screenWidth);
        }else{
            $(imageDom).height(screenHeight);
        }
    }
     */
    // $(imageDom).width($(imageDom).width());
    //$(imageDom).height($(imageDom).height());
    /*var left = ( $(window).scrollLeft() + ($(window).width() - $(imageDom).width()) / 2 );
    var top = ( $(window).scrollTop() + ($(window).height() - $(imageDom).height()) / 2 );
    $(imageDom).css({
        'left':left,
        'top':top,
        'position':'absolute'
    });
     */
    $('#'+this._id_layer).css({
        'height':$(document).height(),
        'width':$(window).width()
    });
    //console.log($(window).scrollTop());
    //console.log($(window).height());
    //console.log($('#'+this._id_image).find('img').height());
    var top = ( $(window).scrollTop() + ($(window).height() - 200) / 2 );
    $('#'+this._id_image).css({
        'top':top
    });
}

HubJS.ui.ImageViewer.prototype._getScreenHeight = function(){
    var height = null;
    if(window.screen != null)
        height = window.screen.availHeight;

    if(window.innerHeight != null)
        height =   window.innerHeight;

    if(document.body != null)
        height = document.body.clientHeight;

    return height;
}

HubJS.ui.ImageViewer.prototype._getScreenWidth = function(){
    var width = null;
    if(window.screen != null)
        width = window.screen.availWidth;

    if(window.innerWidth != null)
        width = window.innerWidth;

    if(document.body != null)
        width = document.body.clientWidth;

    return width;
}


/**
 * @class AjaxHistory
 * @example
 *http://jindo.dev.naver.com/docs/jindo-mobile/archive/latest/source/jindo.m.AjaxHistory.js
 *http://jindo.dev.naver.com/docs/jindo-mobile/archive/latest/sample/latest/jindo.m.AjaxHistory/default.html
 */
HubJS.namespace('HubJS.RealTime');

HubJS.RealTime = function(option){

    }
HubJS.RealTime.prototype.getLocalTS = function(utc_timestamp){
    utc_timestamp = parseInt(utc_timestamp);
    var utc = new Date(utc_timestamp);
    var timeZoneOffset = utc.getTimezoneOffset();
    localTS = utc_timestamp ;

    return localTS;
}


HubJS.RealTime.prototype.getRealTime = function(utc_timestamp, lang){
//    var localTS = this.getLocalTS(utc_timestamp);
    var localTS = parseInt(utc_timestamp);
    var currentTS = new Date().getTime();
    var gapTS = currentTS - localTS;
    var gapSecond = Math.floor(gapTS/1000);

    if(gapSecond < 60){
        switch(lang) {
            case 'KOR' : return '방금 전'; break;
            case 'ENG' : return 'just now'; break;
            case 'JPN' : return 'たった今'; break;
            case 'ZHO' : return '刚刚';break;
            case 'TCH' : return '剛剛';break;
			case 'RUS' : return 'только что'; break;
			case 'DEU' : return 'Gerade eben'; break;			
			case 'FRA' : return "A l'instant"; break;
			case 'SPA' : return 'Recién'; break;
			case 'POR' : return 'agora'; break;
			case 'IND' : return 'baru saja'; break;
			//case 'MYS' : return 'baru sahaja'; break;
			case 'THA' : return 'เมื่อครู่นี้'; break;
			case 'VIE' : return 'vừa xong'; break;
			case 'TUR' : return 'şimdi'; break;
			case 'ITA' : return 'ora'; break;
            case 'ARA' : return 'الآن'; break;
            default : return '방금 전'; break;
        }
    }

    var gapMinute = Math.floor(gapSecond/(60));
    if(gapMinute < 60){
        switch(lang) {
            case 'KOR' : return gapMinute+'분 전'; break;
            case 'ENG' : return gapMinute+'minutes ago'; break;
            case 'JPN' : return gapMinute+'分前'; break;
            case 'ZHO' : return gapMinute+'分钟前';break;
            case 'TCH' : return gapMinute+'分鐘前';break;
			case 'RUS' : return gapMinute+'минут назад'; break;
			case 'DEU' : return 'Vor '+gapMinute+' Minuten'; break;			
			case 'FRA' : return 'Il y a '+gapMinute+' minute(s)' ; break;
			case 'SPA' : return 'Hace '+gapMinute ; break;
			case 'POR' : return gapMinute+' minutos atrás'; break;
			case 'IND' : return gapMinute+' menit yang lalu'; break;
			//case 'MYS' : return gapMinute+' minit lalu'; break;
			case 'THA' : return gapMinute+' นาทีที่แล้ว'; break;
			case 'VIE' : return gapMinute+' phút trước'; break;
			case 'TUR' : return gapMinute+' dakika önce'; break;
			case 'ITA' : return gapMinute+' minuti fa'; break;
            //case 'ARA' : return gapMinute+' دقائق %d قبل '; break;
			case 'ARA' : return ' دقائق ' + gapMinute + ' قبل '; break;
            default : return gapMinute+'분 전'; break;
        }
    }

    var gapHour   = Math.floor(gapSecond/(60*60));
    if(gapHour < 24){
        switch(lang) {
            case 'KOR' : return gapHour+'시간 전'; break;
            case 'ENG' : return gapHour+'hours ago'; break;
            case 'JPN' : return gapHour+'時間前'; break;
            case 'ZHO' : return gapHour+'小时前';break;
            case 'TCH' : return gapHour+'小時前';break;
			case 'RUS' : return gapHour+' часов назад'; break;
			case 'DEU' : return 'Vor '+gapHour+' Stunden'; break;			
			case 'FRA' : return 'Il y a '+gapHour+' heure(s)' ; break;
			case 'SPA' : return 'Hace '+gapHour+' horas'; break;
			case 'POR' : return gapHour+' horas atrás'; break;
			case 'IND' : return gapHour+' jam yang lalu'; break;
			//case 'MYS' : return gapHour+' jam lalu'; break;
			case 'THA' : return gapHour+' ชั่วโมงที่แล้ว'; break;
			case 'VIE' : return gapHour+' giờ trước'; break;
			case 'TUR' : return gapHour+' saat önce'; break;
			case 'ITA' : return gapHour+' ore fa'; break;
            //case 'ARA' : return gapHour+' ساعات %d قبل '; break;
			case 'ARA' : return ' ساعات ' + gapHour + ' قبل '; break;
            default : return gapHour+'시간 전'; break;
        }
    }
    var gapDay    = Math.floor(gapSecond/(60*60*24));
    if(gapDay < 4){
        switch(lang) {
            case 'KOR' : return gapDay+'일 전'; break;
            case 'ENG' : return gapDay+'days ago'; break;
            case 'JPN' : return gapDay+'日前'; break;
            case 'ZHO' : return gapDay+'天前';break;
            case 'TCH' : return gapDay+'天前';break;
			case 'RUS' : return gapDay+' дней назад'; break;
			case 'DEU' : return 'Vor '+gapDay+' Tagen'; break;			
			case 'FRA' : return 'Il y a '+gapDay+' jour(s)'; break;
			case 'SPA' : return 'Hace '+gapDay+' días'; break;
			case 'POR' : return gapDay+' dias atrás'; break;
			case 'IND' : return gapDay+' hari yang lalu'; break;
			//case 'MYS' : return gapDay+' hari lalu'; break;
			case 'THA' : return gapDay+' วันที่แล้ว'; break;
			case 'VIE' : return gapDay+' ngày trước'; break;
			case 'TUR' : return gapDay+' gün önce'; break;
			case 'ITA' : return gapDay+' giorni fa'; break;
            //case 'ARA' : return gapDay+' أيام %d قبل '; break;
			case 'ARA' : return ' أيام ' + gapDay + ' قبل '; break;
            default : return gapDay+'일 전'; break;
        }
    }
    var gapYear    = Math.floor(gapSecond/(60*60*24*365));

    var localDate = new Date(localTS);
    //if(gapYear >= 1){
    var year = localDate.getFullYear();
    var month = localDate.getMonth()+1;
    if(month < 10) month = '0'+month;
    var date = localDate.getDate();
    if(date < 10) date = '0'+date;
    var ret = year + '.'+ month + '.' + date;
    return ret
    //}

    return (localDate.getMonth()+1)+' 월 '+ localDate.getDay() +' 일';

}

HubJS.namespace('HubJS.EmailValid');

HubJS.EmailValid = function(){
	
}

HubJS.EmailValid.prototype.show = function(id){
	$(id).hide();
	$('#HIVEcontainer').hide();
	$('#HIVEfooter').hide();
	$('#emailValid_layer').show();
}
HubJS.EmailValid.prototype.hide = function(id){
	$(id).show();
	$('#HIVEcontainer').show();
	$('#HIVEfooter').show();
	$('#emailValid_layer').hide();
}
HubJS.EmailValid.prototype.set = function(type, value, tag){
	var jdata = {};
	jdata.type = type;
	jdata.value = value;

	var json_data = JSON.stringify(jdata);

	$.ajax({
		url : "/api_user/emailvalid",
		type : "post",
		data:json_data,
		dataType : "json",
		success : function(data) {

			if( data.EmailValid == 'N' ){
				emailValid.show(tag);
			}

		},
		error : function() {

		},
	});
}


//
window['HubJS'] = HubJS;
HubJS['namespace'] = HubJS.namespace;
HubJS['constant'] = HubJS.constant;
HubJS.constant['set'] = HubJS.constant.set;
HubJS.constant['isDefined'] = HubJS.constant.isDefined;
HubJS.constant['get'] = HubJS.constant.get;
//HubJS.Validation.js
HubJS["Validation"] = HubJS.Validation;
HubJS.Validation.prototype["validate"] = HubJS.Validation.prototype.validate;
HubJS.Validation["Email"] = HubJS.Validation.Email;
HubJS.Validation.Email.prototype["isValid"] = HubJS.Validation.Email.prototype.isValid;
HubJS.Validation["Password"] = HubJS.Validation.Password;
HubJS.Validation.Password.prototype["isValid"] = HubJS.Validation.Password.prototype.isValid;
HubJS.Validation["HubId"] = HubJS.Validation.HubId;
HubJS.Validation.HubId.prototype["isValid"] = HubJS.Validation.HubId.prototype.isValid;
//HubJS.crypto.MD5.js
HubJS["crypto"] = HubJS.crypto;
HubJS.crypto["MD5"] = HubJS.crypto.MD5;
HubJS.crypto.MD5.prototype["getHex"] = HubJS.crypto.MD5.prototype.getHex;
//HubJS.ui.SegmentedControl.js
HubJS["ui"] = HubJS.ui;
HubJS["ui"]["SegmentedControl"] = HubJS.ui.SegmentedControl;

//HubJS.ui.Loading.js
HubJS["ui"] = HubJS.ui;
HubJS["ui"]["Loading"] = HubJS.ui.Loading;
HubJS.ui.Loading.prototype["show"] = HubJS.ui.Loading.prototype.show;
HubJS.ui.Loading.prototype["hide"] = HubJS.ui.Loading.prototype.hide;

//HubJS.AjaxHistory.js
HubJS["AjaxHistory"] = HubJS.AjaxHistory;
HubJS["AjaxHistory"].prototype['initialize'] = HubJS.AjaxHistory.prototype.initialize;
HubJS["AjaxHistory"].prototype['destroy'] = HubJS.AjaxHistory.prototype.destroy;
HubJS["AjaxHistory"].prototype['addHistory'] = HubJS.AjaxHistory.prototype.addHistory;
HubJS["AjaxHistory"].prototype['attach'] = HubJS.AjaxHistory.prototype.attach;

//HubJS.Native.js
HubJS["Native"] = HubJS.Native;
HubJS["Native"].prototype['getPicture'] = HubJS.Native.prototype.getPicture;
HubJS["Native"].prototype['getAddressBook'] = HubJS.Native.prototype.getAddressBook;

//HubJS.Native.FB.js
HubJS["Native"]["FB"] = HubJS.Native.FB;
HubJS.Native.FB.prototype['getBaseURL']=HubJS.Native.FB.prototype.getBaseURL;
HubJS.Native.FB.prototype['setAccessToken']=HubJS.Native.FB.prototype.setAccessToken;
HubJS.Native.FB.prototype['getAccessToken']=HubJS.Native.FB.prototype.getAccessToken;
HubJS.Native.FB.prototype['loginCallback']=HubJS.Native.FB.prototype.loginCallback;
HubJS.Native.FB.prototype['init']=HubJS.Native.FB.prototype.init;
HubJS.Native.FB.prototype['login']=HubJS.Native.FB.prototype.login;
HubJS.Native.FB.prototype['api']=HubJS.Native.FB.prototype.api;

//HubJS.ui.Toast.js
HubJS["ui"] = HubJS.ui;
HubJS["ui"]["Toast"] = HubJS.ui.Toast;
HubJS.ui.Toast.prototype["show"] = HubJS.ui.Toast.prototype.show;

//HubJS.ui.TextInput.js
HubJS["ui"] = HubJS.ui;
HubJS["ui"]["TextInput"] = HubJS.ui.TextInput;
HubJS.ui.TextInput.prototype["getPlaceHolderString"] = HubJS.ui.TextInput.prototype.getPlaceHolderString;
HubJS.ui.TextInput.prototype["getValue"] = HubJS.ui.TextInput.prototype.getValue;

//HubJS.ui.Dialog
HubJS["ui"] = HubJS.ui;
HubJS["ui"]["Dialog"] = HubJS.ui.Dialog;
HubJS["ui"]["Dialog"].prototype['show'] = HubJS.ui.Dialog.prototype.show;
HubJS["ui"]["Dialog"].prototype['hide'] = HubJS.ui.Dialog.prototype.hide;
//HubJS.ui.ImageViewer
HubJS["ui"] = HubJS.ui;
HubJS["ui"]["ImageViewer"] = HubJS.ui.ImageViewer;
HubJS["ui"]["ImageViewer"].prototype["show"] = HubJS.ui.ImageViewer.prototype.show;
HubJS["ui"]["ImageViewer"].prototype["hide"] = HubJS.ui.ImageViewer.prototype.hide;

//HubJS.RealTime
HubJS["RealTime"] = HubJS.RealTime;
HubJS["RealTime"].prototype["getLocalTS"] = HubJS.RealTime.prototype.getLocalTS;
HubJS["RealTime"].prototype["getRealTime"] = HubJS.RealTime.prototype.getRealTime;

//HubJS.EmailValid
HubJS["EmailValid"] = HubJS.EmailValid;
HubJS["EmailValid"].prototype["show"] = HubJS.EmailValid.prototype.show;
HubJS["EmailValid"].prototype["hide"] = HubJS.EmailValid.prototype.hide;
HubJS["EmailValid"].prototype["set"] = HubJS.EmailValid.prototype.set;