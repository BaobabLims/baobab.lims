function CustomProjectAddView(){
    var biospecFd = '#archetypes-fieldname-SampleType';
    var biospecSel = '#archetypes-fieldname-SampleType #SampleType';
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
    }

    function init() {
        applyStyles();
        biospecSelection();
    }

    function biospecSelection(){
        $(biospecSel).on('change', function(){
            var biospecUIDs = $(biospecSel).val();
            if(biospecUIDs){
                analysis_cb_uncheck();
                biospecSet(biospecUIDs);
            }
        })
    }

    function biospecSet(uid){
        var d = $.Deferred();
        var requestData = {
            catalog_name: "bika_setup_catalog",
            portal_type: "SampleType",
            UID: uid
        };
        bika.lims.jsonapi_read(requestData, function (data) {
            $.each(data["objects"], function(i, biospec_objects){
                var defs = [];
                var serviceData = biospec_objects["service_data"];
                if(serviceData.length != 0){
                    defs.push(expandServiceBikaListing(serviceData));
                }
            });

        });
    }

    function expandServiceBikaListing(serviceData){
        var d = $.Deferred();
        var services = [];
        var defs = [];
        var expanded_categories = [];
        for(var si = 0; si < serviceData.length; si++){
            var service = serviceData[si];
            services.push(service);
            var th = $("table[form_id='" + service['PointOfCapture'] + "'] " +
                       "th[cat='" + service['CategoryTitle'] + "']");
            if(expanded_categories.indexOf(th) < 0) {
                expanded_categories.push(th);
                var def = $.Deferred();
                def = category_header_expand_handler(th);
                defs.push(def);
            }
        }
        // Call $.when with all deferreds
        $.when.apply(null, defs).then(function () {
            // select services
            for (var si = 0; si < services.length; si++) {
                analysis_cb_check(services[si]['UID'])
            }
            d.resolve();
        });
        return d.promise();
    }

    function analysis_cb_check(uid) {
        /* Called to un-check an Analysis' checkbox as though it were clicked.
         */
        var cb = $("tr[uid='" + uid + "'] " +
                   "input[type='checkbox']");
        $(cb).attr("checked", true);
    }

    function analysis_cb_uncheck() {
        /* Called to un-check an Analysis' checkbox as though it were clicked.
         */
        var cb = $("tr input[type='checkbox']");
        $(cb).removeAttr("checked");
    }

    function category_header_expand_handler(element) {
        /* Deferred function to expand the category with ajax (or not!!)
         on first expansion. duplicated from bika.lims.bikalisting.js, this code
         fires when categories are expanded automatically (eg, when profiles or templates require
         that the category contents are visible for selection)

         Also, this code returns deferred objects, not their promises.

         :param: element - The category header TH element which normally receives 'click' event
         */
        var def = $.Deferred();
        // with form_id allow multiple ajax-categorised tables in a page
        var form_id = $(element).parents("[form_id]").attr("form_id");
        var cat_title = $(element).attr('cat');
        var ar_count = parseInt($("#ar_count").val(), 10);
        // URL can be provided by bika_listing classes, with ajax_category_url attribute.
        var url = $("input[name='ajax_categories_url']").length > 0
          ? $("input[name='ajax_categories_url']").val()
          : window.location.href.split('?')[0];
        // We will replace this element with downloaded items:
        var placeholder = $("tr[data-ajax_category='" + cat_title + "']");

        // If it's already been expanded, ignore
        if ($(element).hasClass("expanded")) {
            def.resolve();
            return def;
        }

        // If ajax_categories are enabled, we need to go request items now.
        var ajax_categories_enabled = $("input[name='ajax_categories']");
        if (ajax_categories_enabled.length > 0 && placeholder.length > 0) {
            var options = {}
            // this parameter allows the receiving view to know for sure what's expected
            options['ajax_category_expand'] = 1;
            options['cat'] = cat_title;
            options['ar_count'] = ar_count;
            options['form_id'] = form_id;
            if ($('.review_state_selector a.selected').length > 0) {
                // review_state must be kept the same after items are loaded
                // (TODO does this work?)
                options['review_state'] = $('.review_state_selector a.selected')[0].id;
            }
            console.log(url);
            $.ajax({url: url, data: options})
              .done(function (data) {
                    var rows = $("<table>"+data+"</table>").find("tr");
                    $("[form_id='" + form_id + "'] tr[data-ajax_category='" + cat_title + "']").replaceWith(rows);
                    $(element).removeClass("collapsed").addClass("expanded");
                    def.resolve();
                })
        }
        else {
            // When ajax_categories are disabled, all cat items exist as TR elements:
            $(element).parent().nextAll("tr[cat='" + cat_title + "']").toggle(true);
            $(element).removeClass("collapsed").addClass("expanded");
            def.resolve();
        }
        return def;
    }

    function applyStyles() {
        $(biospecFd)
            .css('border', '1px solid #cfcfcf')
            .css('background-color', '#efefef')
            .css('padding', '10px')
            .css('margin-bottom', '20px');
    }
}