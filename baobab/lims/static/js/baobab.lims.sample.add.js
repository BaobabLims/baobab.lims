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

        $('tr[fieldname=Kit]').hide();
        $('tr[fieldname=BabyNumber]').hide();
        sampleTypeSelected($('#SampleType_uid').val());

        $('#SampleType_uid').focus(function() {
            var uid = $(this).val();
            sampleTypeSelected(uid);
        });

        if ($('#Unit').val() == "other"){
            $('<div/>').addClass( 'unit_measure_div' )
                .html( $('<input type="textbox" name="customUnit" id="customUnit" />').addClass( 'blurrable firstToFocus customUnit' ) )
                .insertAfter( $("#Unit") );
        }
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
        });

        $('#Unit').change(function(e) {
            if ($(this).val() == "other"){
                e.preventDefault();
                $('<div/>').addClass( 'unit_measure_div' )
                .html( $('<input type="textbox" name="customUnit" id="customUnit" />').addClass( 'blurrable firstToFocus customUnit' ) )
                .insertAfter( this );
            }else{
                $('div.unit_measure_div').remove();
            }
        });

        // console.log('========================')
        var path = window.location.href.split('edit')[0] + '/get_sample_dates';
        // console.log(path)
        var title = $('#breadcrumbs-current').text()
        // console.log(title)

        // var path = window.location.href.split('/base_view')[0] + '/retrieve_date_times';
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: path,
            data: {'title': title}
        }).done(function (data) {
            // console.log('-----------')
            // console.log(data);

            var sampling_date = data['sampling_date']
            if (sampling_date) {
                var final_sampling_date = getDatePickerDateAndTime(sampling_date)
                $('#SamplingDate').val(final_sampling_date)
            }

            var frozen_time = data['frozen_time']
            if (frozen_time) {
                var final_frozen_time = getDatePickerDateAndTime(frozen_time)
                $('#FrozenTime').val(final_frozen_time)
            }
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
              } else {
                $('tr[fieldname=BabyNumber]').hide();
                $('#BabyNumber option:first-child').attr("selected", "selected");
              }

              var theSampleType = $('#SampleType').attr("val_check").toLowerCase();
              var regex = new RegExp('(collection|heel|card)+((?!delayed|clotted).)*$');
              if (uid && regex.test(theSampleType)) {
                $('tr[fieldname=FrozenTime]').hide();
              } else {
                $('tr[fieldname=FrozenTime]').show();
              }

              var parentBiospecimenUid = $('#LinkedSample_uid').attr('value')
              // var sampleTypeUid = $('#SampleType_uid').attr('value')
              if (uid && !parentBiospecimenUid) {
                var rgx = new RegExp('(collection|heel)');
                if (!rgx.test(theSampleType)) {
                    $("#SampleType").each( function() {
                      alert("If you are creating a parent biospecimen, please search and choose a 'Collection' sample type or 'Heal Prick'.");
                    });
                }
              }
            }
        });
    }

    function getDatePickerDateAndTime(plone_date){
        try{
            // console.log('-----------------------')
            var new_date = new Date(plone_date)

            var gmt_format_date = getGMTFormatDate(plone_date)
            // console.log(gmt_format_date)

            return gmt_format_date  //final_date_and_time
        }
        catch(err){
            console.log("Error: " + err.message)
            return plone_date
        }

    }

    function getGMTFormatDate(plone_date_string){

        var pieces = plone_date_string.split(/[-/ :]/)

        return [pieces[0], pieces[1], pieces[2]].join('-') + ' ' + [pieces[3], pieces[4]].join(':')
    }

}
