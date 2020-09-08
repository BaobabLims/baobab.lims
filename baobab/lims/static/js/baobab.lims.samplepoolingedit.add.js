function BaobabSamplePoolingEditView() {

    var that = this;

    that.load = function () {

        setDateCreated();
        $('.reverse_sample_pooling').click(function(event){
            event.preventDefault();
            reverse_pooling();
        });

    };

    function setDateCreated(){
        var path = window.location.href.split('/sample_poolings')[0];
        var uid = $('#archetypes-fieldname-DateCreated').attr('data-uid');

        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: path + '/ajax_get_samplepoolingdata',
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

    function reverse_pooling(){
        var reverse_pooling = confirm("This will wipe out the current sample pooling.  Are you sure?");
        if (reverse_pooling == true) {

            console.log('We are about to start the reversal======')

            // var final_data = JSON.stringify({'object_uid': $('#sample_pooling_obj_uid')});
            var final_data = JSON.stringify({'object_uid': $('#archetypes-fieldname-title').attr('data-uid')});
            var path = window.location.href.split('/sample_poolings')[0];

            $.ajax({
                dataType: "json",
                contentType: 'application/json',
                url: path + '/ajax_reverse_pooling',
                data: {'pooling_data': final_data},
                success: function (data) {

                    console.log('--------------Successful.');
                    console.log(data);
                    console.log(data.url);
                    window.location.href = data.url;
                },
                error: function (data) {
                    console.log('--------------Error has been reached.');
                    console.log(data);
                    console.log(data.responseText);
                    var error_response = JSON.parse(data.responseText);

                    $("#error_message").css("display", "block");
                    $("#error_message").find('.response_header').css("display", "block");
                    $(".response_li").remove();
                    $("#error_list").append('<li class="response_li" style="color: red;">' + error_response.error_message + '</li>');
                    alert(error_response.error_message);
                },
            });

        }
    }
}