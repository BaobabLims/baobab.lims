function BaobabCollectionRequestEditView() {

    var that = this;

    that.load = function () {
        setUpUI();
    };

    function setUpUI(){
        setUpFormTabs();
        setUpSaveButtons();
        setNotEditable();
    }

    function setNotEditable(){
        $('#Client').attr("disabled", true);
        $('#RequestNumber').attr("disabled", true);
        $('#DateOfRequest').attr("disabled", true);
        $('#CollectMicrobeSamples').attr("disabled", true);
        $('#CollectHumanSamples').attr("disabled", true);
        $('#NumberRequested').attr("disabled", true);

        if ($('#ResultOfEvaluation').val() != "") {
            $('#DateEvaluated').attr("disabled", true);
            $('#ResultOfEvaluation').attr("disabled", true);
            $('#ReasonForEvaluation').attr("disabled", true);
        }
    }

    function setUpSaveButtons(){
        $('#baobab_collection_request_edit').find(':submit').remove();

        var buttons = '\
            <div class="save_collectionrequest_approval">\
                <button type="button" class="save_collectionrequest_approval" id="save_collectionrequest_approval">Save Collection Request Approval</button>\
            </div>\
        ';
        $('#fieldset-evaluation').append(buttons);

        $('#save_collectionrequest_approval').click(function(event){
        // $('#save_collectionrequest_approval').unbind('click').bind('click', function(event){
            save_collectionrequest_approval();
        });
    }

    function save_collectionrequest_approval() {
        var collectionrequest_data = get_approve_collection_request_data();
        save_collection_request_approval(collectionrequest_data);
    }

    function get_approve_collection_request_data(){
        var collectionrequest_data = {};

        collectionrequest_data['approval_data_details'] = get_collectionrequest_details();
        collectionrequest_data['approval_data_microbe_rows'] = get_microbe_collection();
        collectionrequest_data['approval_data_human_rows'] = get_human_collection();

        return collectionrequest_data;

    }

    function save_collection_request_approval(collectionrequest_data){
        var final_data = JSON.stringify(collectionrequest_data);
        var path = window.location.href.split('/collection_requests')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_approve_collection_request',
            data: {'approval_data': final_data},
            success: function (data) {
                // console.log('--------------Successful.');
                // console.log(data);
                // console.log(data.url);
                window.location.href = data.url;
            },
            error: function (data) {
                // console.log('--------------Error has been reached.');
                // console.log(data);
                // console.log(data.responseText);
                var error_response = JSON.parse(data.responseText);

                $("#error_message").css("display", "block");
                $("#error_message").find('.response_header').css("display", "block");
                $(".response_li").remove();
                $("#error_list").append('<li class="response_li" style="color: red;">' + error_response.error_message + '</li>');
                alert(error_response.error_message);
            },
        });
    }

    function get_collectionrequest_details(){
        var approval_data_details = {};
        approval_data_details['collection_request_uid'] = $('#archetypes-fieldname-NumberRequested').attr('data-uid');
        approval_data_details['date_of_request'] = $("#DateOfRequest").val();
        approval_data_details['date_evaluated'] = $("#DateEvaluated").val();
        approval_data_details['result_of_evaluation'] = $("#ResultOfEvaluation").val();
        approval_data_details['reason_for_evaluation'] = $("#ReasonForEvaluation").val();

        return approval_data_details;
    }

    function get_microbe_collection(){
        var microbe_collectionrequests = [];
        $('.microbe-collectionrequest-rows').each(function(alqt_index, microbe_collectionrequest_row){
            var id = $(microbe_collectionrequest_row).attr('id');
            var request_approval = $(microbe_collectionrequest_row).find('.microbe-request-approval').val();

            microbe_collectionrequests.push(
                {
                  'uid': id,
                  'approval': request_approval,
                }
            );
        });
        return microbe_collectionrequests;
    }

    function get_human_collection(){
        var human_collectionrequests = [];
        $('.human-collectionrequest-rows').each(function(alqt_index, human_collectionrequest_row){

            var id = $(human_collectionrequest_row).attr('id');
            var request_approval = $(human_collectionrequest_row).find('.human-request-approval').val();

            human_collectionrequests.push(
                {
                  'uid': id,
                  'approval': request_approval,
                }
            );
        });
        return human_collectionrequests;
    }

    function setUpFormTabs(){
        $('#fieldsetlegend-client-information span').trigger("click");
        $('#fieldsetlegend-client-information').css('background-color', '#ffffff');
        $('#fieldsetlegend-sample-requests').css('background-color', '#ccc');
        $('#fieldsetlegend-evaluation').css('background-color', '#ccc');

        $('#fieldset-client-information').css('display', 'block');
        $('#fieldset-sample-requests').css('display', 'none');
        $('#fieldset-evaluation').css('display', 'none');

        $('#fieldsetlegend-client-information').click(function(){
            $('#fieldsetlegend-client-information').css('background-color', '#ffffff');
            $('#fieldsetlegend-sample-requests').css('background-color', '#ccc');
            $('#fieldsetlegend-evaluation').css('background-color', '#ccc');

            $('#fieldset-client-information').css('display', 'block');
            $('#fieldset-sample-requests').css('display', 'none');
            $('#fieldset-evaluation').css('display', 'none');
        });

        $('#fieldsetlegend-sample-requests').click(function(){
            $('#fieldsetlegend-client-information').css('background-color', '#ccc');
            $('#fieldsetlegend-sample-requests').css('background-color', '#ffffff');
            $('#fieldsetlegend-evaluation').css('background-color', '#ccc');

            $('#fieldset-client-information').css('display', 'none');
            $('#fieldset-sample-requests').css('display', 'block');
            $('#fieldset-evaluation').css('display', 'none');
        });

        $('#fieldsetlegend-evaluation').click(function(){
            $('#fieldsetlegend-client-information').css('background-color', '#ccc');
            $('#fieldsetlegend-sample-requests').css('background-color', '#ccc');
            $('#fieldsetlegend-evaluation').css('background-color', '#ffffff');

            $('#fieldset-client-information').css('display', 'none');
            $('#fieldset-sample-requests').css('display', 'none');
            $('#fieldset-evaluation').css('display', 'block');
        });
    }

}