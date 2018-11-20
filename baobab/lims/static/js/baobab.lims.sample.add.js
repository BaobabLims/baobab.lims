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
        // $('tr[fieldname=BabyNumber]').hide();
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

        // var requestData = {
        //     catalog_name: "portal_catalog",
        //     portal_type: "Sample",
        //     UID: $('#LinkedSample_uid').val()
        // };
        // window.bika.lims.jsonapi_read(requestData, function (data) {
        //     if (data.success && data.total_objects > 0) {
        //         console.log('=====10---------')
        //         console.log(data.objects[0])
        //
        //         var creation_date = data.objects[0]['creation_date']
        //         var cfg_date_time = data.objects[0]['CfgDateTime']
        //
        //         var final_creation_date = getDatePickerDateAndTime(creation_date)
        //         var final_cfg_date_time = getDatePickerDateAndTime(cfg_date_time)
        //
        //         $('#DateCreated').val(final_creation_date)
        //         $('#CfgDateTime').val(final_cfg_date_time)
        //
        //     }
        // });

        // var path = window.location.href.split('/base_view')[0] + '/retrieve_date_times';
        // $.ajax({
        //     type: 'GET',
        //     dataType: 'json',
        //     url: path,
        //     data: {'locTitle': $('#StorageLocation').val()}
        // }).done(function (data) {
        //     console.log(data);
        // })

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

    function getDatePickerDateAndTime(creation_date){
        new_date = new Date(creation_date)

        var gmt_format_date = getGMTFormatDate(creation_date)

        var new_date = new Date(gmt_format_date)
        final_date_and_time = getDateString(new_date)

        return final_date_and_time
    }

    function getGMTFormatDate(plone_date_string){
        if (plone_date_string.includes('GMT')){
            gmt_split = plone_date_string.split('GMT')
            date_part = gmt_split[0].trim()
            gmt_part = gmt_split[1]
        } else {
            gmt_part = null
            date_part = plone_date_string
        }

        var pieces = date_part.split(/[-/ :]/)
        var month_string = getMonthString(pieces[1])

        var gmt_format_date = month_string + ' ' + pieces[2] + ', ' + pieces[0] + ' ' + pieces[3] + ':' + pieces[4]
        if (gmt_part != null){
            gmt_format_date = gmt_format_date + ' GMT' + gmt_part
        }

        return gmt_format_date
    }

    function getMonthString(month_number){
        var months = {
                    '01': 'January',
                    '02': 'February',
                    '03': 'March',
                    '04': 'April',
                    '05': 'May',
                    '06': 'June',
                    '07': 'July',
                    '08': 'August',
                    '09': 'September',
                    '10': 'October',
                    '11': 'November',
                    '12': 'December'
                };

        return months[month_number]
    }

    function getDateString(date){
        var date_portion = [
          date.getFullYear(),
          ('0' + (date.getMonth() + 1)).slice(-2),
          ('0' + date.getDate()).slice(-2)
        ].join('-');

        var time_portion = [
            ('0' + (date.getHours() + 1)).slice(-2),
            ('0' + date.getMinutes()).slice(-2)
        ].join(':');

        var final_date_and_time = date_portion + ' ' + time_portion

        return final_date_and_time
    }

}
