function BaobabSampleCentrifugationEditView() {

    var that = this;

    that.load = function () {
        //
        // alert('This is test edit');
        // console.log('Log edit');
        setDateCreated();

    };

    function setDateCreated(){
        var path = window.location.href.split('/centrifugations')[0];
        var uid = $('#archetypes-fieldname-DateCreated').attr('data-uid');

        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: path + '/ajax_get_centrifugation_data',
            data: {UID: uid}
        }).done(function (data) {
            var date_created = data['date_created']
            if (date_created) {
                var final_sampling_date = getDatePickerDateAndTime(date_created)
                $('#DateCreated').val(final_sampling_date)
            }
        });
    }

    function getDatePickerDateAndTime(plone_date){
        try{
            var gmt_format_date = getGMTFormatDate(plone_date);
            return gmt_format_date;
        }
        catch(err){
            return plone_date;
        }

    }

    function getGMTFormatDate(plone_date_string){

        var pieces = plone_date_string.split(/[-/ :]/)
        return [pieces[0], pieces[1], pieces[2]].join('-') + ' ' + [pieces[3], pieces[4]].join(':')
    }
}