function BaobabSampleView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        $('#Project_uid').focus(function() {
            var uid = $(this).val();
            var element = $("#Kit");
            filterKitByProject(element, "getParentUID", uid);
        });

        $('#SampleType_uid').focus(function() {
            $('tr[fieldname=BabyNumber]').hide();
            var uid = $(this).val();
            sampleTypeSelected(uid);
        });

        $('input[type=submit]').on('click', function (event) {
            var path = window.location.href.split('/base_view')[0] + '/update_boxes';
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: {'locTitle': $('#StorageLocation').val()}
            }).done(function (data) {
                console.log(data);
            })
        })

    };

    function filterKitByProject(element, filterKey, filterValue) {
        var query = $.parseJSON($(element).attr('base_query'));
        query[filterKey] = filterValue;
        var options = $.parseJSON($(element).attr('combogrid_options'));
        $(element).attr('base_query', $.toJSON(query));
        $(element).attr("combogrid_options", $.toJSON(options));
        //referencewidget_lookups($(element));

        options.url = window.location.href.split("/edit")[0] + "/" + options.url;
        options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
        options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
        options.url = options.url + "&base_query=" + $.toJSON(query);
        options.url = options.url + "&search_query=" + $(element).attr("search_query");
        options.url = options.url + "&colModel=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).colModel);
        options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['search_fields']);
        options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['discard_empty']);
        options.force_all = "false";
        $(element).combogrid(options);
        $(element).attr("search_query", "{}");
    }

    function sampleTypeSelected(uid) {
        // Hides or Displays the BabyNumber field depending on boolean value of
        // HasBabyNumber on the SampleType
        request_data = {
          catalog_name: 'portal_catalog',
          portal_type: 'SampleType',
          UID: uid,
          inactive_state: 'active'
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            var sampleType;
            if (data.success && data.total_objects === 1) {
              sampleType = data.objects[0];
              var sampletype_hasBabyNumber = sampleType['HasBabyNumber']
              if (sampletype_hasBabyNumber){
                     $('tr[fieldname=BabyNumber]').show();
                  }
              }
            });
    }
}
