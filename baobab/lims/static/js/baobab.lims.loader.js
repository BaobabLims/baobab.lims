'use strict';
window.baobab = window.baobab || { lims: {} };
window.baobab['baobab']={};
window.jarn.i18n.loadCatalog("baobab.lims");
var _s = window.jarn.i18n.MessageFactory("baobab.lims");

/**
 * Dictionary of JS objects to be loaded at runtime.
 * The key is the DOM element to look for in the current page. The
 * values are the JS objects to be loaded if a match is found in the
 * page for the specified key. The loader initializes the JS objects
 * following the order of the dictionary.
 */
window.baobab.lims.controllers =  {
    ".portaltype-samplebatch":
        ['BaobabBiospecimensView', 'BaobabSampleBatchEditView'],
    ".portaltype-biospecimens":
        ['BaobabBiospecimensView'],
    ".template-ar_add #analysisrequest_edit_form":
        ['CustomAnalysisRequestAddView'],
    "#kit-printview-wrapper":
        ['KitPrintView'],
    "#project-base-edit":
        ['CustomProjectAddView'],
    "#kittemplate-base-edit":
        ['ComputeKitTemplatePrice'],
    ".portaltype-inventoryorder.template-base_edit":
        ['OrderEditView'],
    "#order_publish_container":
        ['OrderPublishView'],
    ".portaltype-sampleshipment":
        ['BaobabSampleShipmentView'],
    "#baobab_sample_shipment_edit":
        ['BaobabSampleShipmentEditView'],
    ".portaltype-virussample":
        ['VirusSampleAddView'],
    ".portaltype-sample":
        ['BaobabSampleView'],
    ".portaltype-freezer": ["BaobabFreezerView"],
    ".portaltype-viralgenomicanalysis": ['ViralGenomicAnalysisAddView'],
    "#fieldset-virus-sample-aliquot": ['VirusSampleAliquotAddView'],
};

/**
 * Initializes only the js controllers needed for the current view.
 * Initializes the JS objects from the controllers dictionary for which
 * there is at least one match with the dict key. The JS objects are
 * loaded in the same order as defined in the controllers dict.
 */
window.baobab.lims.initview = function() {
    var loaded = new Array();
    var controllers = window.baobab.lims.controllers;
    for (var key in controllers) {
        if ($(key).length) {
            controllers[key].forEach(function(js) {
                if ($.inArray(js, loaded) < 0) {
                    console.debug('[baobab.lims.loader] Loading '+js);
                    try {
                        var obj = new window[js]();
                        obj.load();
                        // Register the object for further access
                        window.baobab.lims[js]=obj;
                        loaded.push(js);
                    } catch (e) {
                       // statements to handle any exceptions
                       var msg = '[baobab.lims.loader] Unable to load '+js+": "+ e.message +"\n"+e.stack;
                       console.warn(msg);
                       window.bika.lims.error(msg);
                    }
                }
            });
        }
    }
    return loaded.length;
};

window.baobab.lims.initialized = false;

/**
 * Initializes all baobab.lims js stuff
 */
window.baobab.lims.initialize = function() {
    if (bika.lims.initialized == true) {
        var len = window.baobab.lims.initview();
        window.baobab.lims.initialized = true;
        return len;
    }
    // We should wait after bika.lims being initialized
    setTimeout(function() {
        return window.baobab.lims.initialize();
    }, 500);
};

(function( $ ) {
$(document).ready(function(){

    // Initializes baobab.lims
    var length = window.baobab.lims.initialize();
});
}(jQuery));
