'use strict';
window.bika = window.bika || { lims: {} };
window.bika['sanbi']={};
window.jarn.i18n.loadCatalog("bika.sanbi");
var _s = window.jarn.i18n.MessageFactory("bika.sanbi");

/**
 * Dictionary of JS objects to be loaded at runtime.
 * The key is the DOM element to look for in the current page. The
 * values are the JS objects to be loaded if a match is found in the
 * page for the specified key. The loader initializes the JS objects
 * following the order of the dictionary.
 */
window.bika.sanbi.controllers =  {

    ".template-ar_add #analysisrequest_edit_form":
        ['CustomAnalysisRequestAddView'],

    ".supplyex_add":
        ['CustomSupplyExAddView'],
};

/**
 * Initializes only the js controllers needed for the current view.
 * Initializes the JS objects from the controllers dictionary for which
 * there is at least one match with the dict key. The JS objects are
 * loaded in the same order as defined in the controllers dict.
 */
window.bika.sanbi.initview = function() {
    var loaded = new Array();
    var controllers = window.bika.sanbi.controllers;
    for (var key in controllers) {
        if ($(key).length) {
            controllers[key].forEach(function(js) {
                if ($.inArray(js, loaded) < 0) {
                    console.debug('[bika.sanbi.loader] Loading '+js);
                    try {
                        var obj = new window[js]();
                        obj.load();
                        // Register the object for further access
                        window.bika.sanbi[js]=obj;
                        loaded.push(js);
                    } catch (e) {
                       // statements to handle any exceptions
                       var msg = '[bika.sanbi.loader] Unable to load '+js+": "+ e.message +"\n"+e.stack;
                       console.warn(msg);
                       window.bika.lims.error(msg);
                    }
                }
            });
        }
    }
    return loaded.length;
};

window.bika.sanbi.initialized = false;

/**
 * Initializes all bika.sanbi js stuff
 */
window.bika.sanbi.initialize = function() {
    if (bika.lims.initialized == true) {
        return window.bika.sanbi.initview();
    }
    // We should wait after bika.lims being initialized
    setTimeout(function() {
        return window.bika.sanbi.initialize();
    }, 500);
};

(function( $ ) {
$(document).ready(function(){

    // Initializes bika.sanbi
    var length = window.bika.sanbi.initialize();
    window.bika.sanbi.initialized = true;

});
}(jQuery));
