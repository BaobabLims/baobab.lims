function BaobabTransportView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        setUpUI();
    };

    function setUpUI() {
        if ($('#Conformance').val() != 'No') {
            $('#archetypes-fieldname-NonConformities').hide();
        }

        $('#Conformance').change(function () {
            if ($('#Conformance').val() == 'No') {
                $('#archetypes-fieldname-NonConformities').show();
            } else {
                $('#archetypes-fieldname-NonConformities').hide();
            }
        });

        setTransportDates();
    }

    function setTransportDates(){
        var path = window.location.href.split('transports')[0] + '/get_transport_dates';
        var uid = $('#archetypes-fieldname-ApplicationNumber').attr('data-uid');

        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: path,
            data: {UID: uid}
        }).done(function (data) {
            var departure_date = data['departure_date']
            if (departure_date) {
                var final_departure_date = getDatePickerDateAndTime(departure_date)
                $('#DepartureDate').val(final_departure_date)
            }

            var arrival_date = data['arrival_date']
            if (arrival_date) {
                var final_arrival_date = getDatePickerDateAndTime(arrival_date)
                $('#ArrivalDate').val(final_arrival_date)
            }
        })
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