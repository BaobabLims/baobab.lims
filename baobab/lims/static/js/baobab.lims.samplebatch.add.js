function BaobabSampleBatchEditView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        // console.log('=============')
        // console.log($('#title').val())

        var requestData = {
            catalog_name: "bika_catalog",
            portal_type: "SampleBatch",
            Title: $('#title').val()
        };
        window.bika.lims.jsonapi_read(requestData, function (data) {
            if (data.success && data.total_objects > 0) {

                // console.log(data.objects[0])

                var creation_date = data.objects[0]['creation_date']
                if (creation_date){
                    var final_creation_date = getDatePickerDateAndTime(creation_date)
                    $('#DateCreated').val(final_creation_date)
                }

                var cfg_date_time = data.objects[0]['CfgDateTime']
                if (cfg_date_time) {
                    var final_cfg_date_time = getDatePickerDateAndTime(cfg_date_time)
                    $('#CfgDateTime').val(final_cfg_date_time)
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