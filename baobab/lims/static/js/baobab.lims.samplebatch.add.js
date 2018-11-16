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

                console.log(data.objects[0])

                var creation_date = data.objects[0]['creation_date']
                var cfg_date_time = data.objects[0]['CfgDateTime']

                var final_creation_date = getDatePickerDateAndTime(creation_date)
                var final_cfg_date_time = getDatePickerDateAndTime(cfg_date_time)

                $('#DateCreated').val(final_creation_date)
                $('#CfgDateTime').val(final_cfg_date_time)

            }
        });
    }

    function getDatePickerDateAndTime(creation_date){
        console.log('-----------------------')
        var new_date = new Date(creation_date)

        var gmt_format_date = getGMTFormatDate(creation_date)
        console.log(gmt_format_date)

        // var new_date = new Date(gmt_format_date)
        // console.log(new_date)
        // final_date_and_time = getDateString(new_date)
        // console.log(final_date_and_time)

        return gmt_format_date  //final_date_and_time
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
        // var month_string = getMonthString(pieces[1])
        //
        // var gmt_format_date = month_string + ' ' + pieces[2] + ', ' + pieces[0] + ' ' + pieces[3] + ':' + pieces[4]
        // if (gmt_part != null){
        //     gmt_format_date = gmt_format_date// + ' GMT' + gmt_part
        // }

        return_date = [pieces[0], pieces[1], pieces[2]].join('-') + ' ' + [pieces[3], pieces[4]].join(':')
        return return_date

        //return gmt_format_date
    }

    // function getMonthString(month_number){
    //     var months = {
    //                 '01': 'January',
    //                 '02': 'February',
    //                 '03': 'March',
    //                 '04': 'April',
    //                 '05': 'May',
    //                 '06': 'June',
    //                 '07': 'July',
    //                 '08': 'August',
    //                 '09': 'September',
    //                 '10': 'October',
    //                 '11': 'November',
    //                 '12': 'December'
    //             };
    //
    //     return months[month_number]
    // }

    // function getDateString(date){
    //     var date_portion = [
    //       date.getFullYear(),
    //       ('0' + (date.getMonth() + 1)).slice(-2),
    //       ('0' + date.getDate()).slice(-2)
    //     ].join('-');
    //
    //     var time_portion = [
    //         ('0' + (date.getHours() + 1)).slice(-2),
    //         ('0' + date.getMinutes()).slice(-2)
    //     ].join(':');
    //
    //     var final_date_and_time = date_portion + ' ' + time_portion
    //
    //     return final_date_and_time
    // }

}