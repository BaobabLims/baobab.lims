function BaobabCollectionRequestView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        setUpUI();
    };

    function setUpUI(){
        var fieldset_sample_requests = $('#fieldset-sample-requests');
        removeControlsAndButtons();
        addMicrobeSampleRequestTable(fieldset_sample_requests);
        addHumanSampleRequestTable(fieldset_sample_requests);
        addSaveAndCancelButtons(fieldset_sample_requests);
        setNotEditable();
    }

    function removeControlsAndButtons(){
        $('#collectionrequest-base-edit').find(':submit').remove();
        $('#archetypes-fieldname-MicrobeSampleRequests').hide();
        $('#archetypes-fieldname-HumanSampleRequests').hide();
    }

    function addMicrobeSampleRequestTable(fieldset_sample_requests){
        $(fieldset_sample_requests).append('<div class="div-microbe-request-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        $('.div-microbe-request-samples').append('<label for="div-microbe-request-samples">Microbe Request Sample</label>');

        $('.div-microbe-request-samples').append('<table class="tbl-microbe-request-samples"><thead class="head-microbe-request-samples"></thead><tbody class="body-microbe-request-samples"></tbody></table>');

        addMicrobeTableHeader($('.head-microbe-request-samples'));
        appendMicrobeSampleRequestTableRow($('.body-microbe-request-samples'));
        addMicrobeTableRowManageButtons($('.div-microbe-request-samples'));

        if($('#CollectMicrobeSamples').prop("checked") == false){
            $('.div-microbe-request-samples').hide();
        }

        addToggleMicrobeTableVisibility();
    }

    function addToggleMicrobeTableVisibility(){
        $('#CollectMicrobeSamples').click(function(){
            if($(this).prop("checked") == true){
                // console.log("Checkbox is checked.");
                $('.div-microbe-request-samples').show();
            }

            else if($(this).prop("checked") == false){
                // console.log("Checkbox is unchecked.");
                $('.div-microbe-request-samples').hide();
            }
        });
    }

    function addHumanSampleRequestTable(fieldset_sample_requests){
        $(fieldset_sample_requests).append('<div class="div-human-request-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        $('.div-human-request-samples').append('<label for="div-human-request-samples">Human Request Sample</label>');

        $('.div-human-request-samples').append('<table class="tbl-human-request-samples"><thead class="head-human-request-samples"></thead><tbody class="body-human-request-samples"></tbody></table>');

        addHumanTableHeader($('.head-human-request-samples'));
        appendHumanSampleRequestTableRow($('.body-human-request-samples'));
        addHumanTableRowManageButtons($('.div-human-request-samples'));

        if($('#CollectHumanSamples').prop("checked") == false){
            $('.div-human-request-samples').hide();
        }

        addToggleHumanTableVisibility();
    }

    function addMicrobeTableHeader(table_header){
        var microbe_table_header_row = '\
            <tr>\
                <th>Identification</th>\
                <th>Strain</th>\
                <th>Origin</th>\
                <th>Sample Type</th>\
                <th>Phenotype</th>\
            </tr>\
        ';

        $(table_header).append(microbe_table_header_row);
    }

    function appendMicrobeSampleRequestTableRow(table_body){

        var collectionrequest_rows = $('.microbe-collectionrequest-rows');
        var row_count = collectionrequest_rows.length + 1;
        const first_row = 1;

        var table_row = '\
            <tr class="microbe-collectionrequest-rows" id="microbe_collectionrequest_row_' + row_count + '">\
                <td><input type="text" class="microbe-collectionrequest-row-identification" id="microbe_collectionrequest_identification_' + row_count + '" /></td>\
                <td><select class="microbe-collectionrequest-row-strain" id="microbe_collectionrequest_strain_' + row_count + '">\
                    <option value=0>-- Select Strain --</option>\
                </select></td>\
                <td>\
                    <select  class="microbe-collectionrequest-row-origin" id="microbe_collectionrequest_origin_' + row_count + '">\
                        <option value="">-- Select Origin --</option>\
                        <option value="human">-- Human --</option>\
                        <option value="plant">-- Plant --</option>\
                        <option value="animal">-- Animal --</option>\
                        <option value="environment">-- Environment --</option>\
                   </select>\
                </td>\
                <td><select class="microbe-collectionrequest-row-sample-type" id="microbe_collectionrequest_sample_type_' + row_count + '">\
                    <option value=0>-- Select Sample Type --</option>\
                </select></td>\
                <td><select class="microbe-collectionrequest-row-phenotype" id="microbe_collectionrequest_phenotype_' + row_count + '">\
                    <option value="">-- Select Phenotype --</option>\
                    <option value="Unknown">-- Unknown--</option>\
                    <option value="WildType">-- WildType --</option>\
                    <option value="Recombinant">-- Recombinant--</option>\
                </select></td>\
            </tr>\
        ';

        if (row_count <= first_row) {
            $('.' + 'body-microbe-request-samples').append(table_row);
        } else {
            $('.' + 'body-microbe-request-samples' + ' tr:last').after(table_row);
        }
        populate_dropdowns('microbe_collectionrequest_sample_type_' + row_count, 'sampletypes');
        populate_dropdowns('microbe_collectionrequest_strain_' + row_count, 'strains');
    }

    function addMicrobeTableRowManageButtons(div){
        var buttons = '\
            <div class="microbe-request-samples-table-buttons">\
                <button type="button" class="extra-microbe-request-samples-row">Add New Row</button>\
                <button type="button" class="remove-last-microbe-request-samples-row">Remove Last Row</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.extra-microbe-request-samples-row').click(function(event){
            event.preventDefault();
            var table_body = $('.body-microbe-request-samples-samples');
            appendMicrobeSampleRequestTableRow(table_body);
        });

        $('.remove-last-microbe-request-samples-row').click(function(event){
            event.preventDefault();
            $('.' + 'body-microbe-request-samples' + ' tr:last').remove();
        });
    }

    //This is the code to add a human sample request table and its rows.
    function addHumanTableHeader(table_header){
        var human_table_header_row = '\
            <tr>\
                <th>Barcode</th>\
                <th>Sample Type</th>\
                <th>Sample Package</th>\
                <th>Volume</th>\
                <th>Unit</th>\
            </tr>\
        ';

        $(table_header).append(human_table_header_row);
    }

    function appendHumanSampleRequestTableRow(){

        var collectionrequest_rows = $('.human-collectionrequest-rows');
        var row_count = collectionrequest_rows.length + 1;
        const first_row = 1;

        var table_row = '\
            <tr class="human-collectionrequest-rows" id="human_collectionrequest_row_' + row_count + '">\
                <td><input type="text" class="human-collectionrequest-row-barcode" id="human_collectionrequest_barcode_' + row_count + '" /></td>\
                <td><select class="human-collectionrequest-row-sample-type" id="human_collectionrequest_sample_type_' + row_count + '">\
                    <option value=0>-- Select Sample Type --</option>\
                </select></td>\
                <td><select class="human-collectionrequest-row-sample-package" id="human_collectionrequest_sample_package_' + row_count + '">\
                    <option value=0>-- Select Sample Package --</option>\
                </select></td>\
                <td><input type="text" class="human-collectionrequest-row-volume" id="human_collectionrequest_volume_' + row_count + '" /></td>\
                <td><select class="human-collectionrequest-row-unit" id="human_collectionrequest_unit_' + row_count + '">\
                    <option value="">-- Select Unit --</option>\
                    <option value="ml">-- ml --</option>\
                    <option value="g">-- g --</option>\
                    <option value="mg">-- mg --</option>\
                </select></td>\
            </tr>\
        ';

        if (row_count <= first_row) {
            $('.body-human-request-samples').append(table_row);
        } else {
            $('.' + 'body-human-request-samples' + ' tr:last').after(table_row);
        }
        populate_dropdowns('human_collectionrequest_sample_type_' + row_count, 'sampletypes');
        populate_dropdowns('human_collectionrequest_sample_package_' + row_count, 'sample_packages');
    }

    function addHumanTableRowManageButtons(div){

        var buttons = '\
            <div class="human-request-samples-table-buttons">\
                <button type="button" class="extra-human-request-samples-row">Add New Row</button>\
                <button type="button" class="remove-last-human-request-samples-row">Remove Last Row</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.extra-human-request-samples-row').click(function(event){
            event.preventDefault();
            var table_body = $('.body-human-request-samples-samples');
            appendHumanSampleRequestTableRow(table_body);
        });

        $('.remove-last-human-request-samples-row').click(function(event){
            event.preventDefault();
            $('.' + 'body-human-request-samples' + ' tr:last').remove();
        });
    }

    function addToggleHumanTableVisibility(){
        $('#CollectHumanSamples').click(function(){
            if($(this).prop("checked") == true){
                // console.log("Checkbox is checked.");
                $('.div-human-request-samples').show();
            }

            else if($(this).prop("checked") == false){
                // console.log("Checkbox is unchecked.");
                $('.div-human-request-samples').hide();
            }
        });
    }

    function addSaveAndCancelButtons(div){
        var buttons = '\
            <div class="savecancel_centrifugations_buttons">\
                <button class="save-collectionrequest">Save Collection Request</button>\
                <button class="cancel-collectionrequest" name="form.button.cancel">Cancel</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.save-collectionrequest').click(function(event){
            event.preventDefault();
            save_collectionrequest();
        });
    }


    function setNotEditable(){
        $('#DateEvaluated').attr("disabled", true);
        $('#ResultOfEvaluation').attr("disabled", true);
        $('#ReasonForEvaluation').attr("disabled", true);
    }

    function populate_dropdowns(dropdown_id, populate_type){
        var path = window.location.href.split('/collection_requests')[0];
        var url_path = path + '/ajax_get_' + populate_type;

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             // url: path + '/ajax_get_' + populate_type,
             url: url_path,
             success: function (data) {
                 // console.log('---------------dropdowns');
                 // console.log(data);
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + dropdown_id).append($('<option>').val(key).text(value));
                    });
                });
             },
             error: function (jqXHR, textStatus, errorThrown) {
                 console.log('This is the error');
                 console.log(jqXHR);
                 console.log(textStatus);
                 console.log(errorThrown);

             }
         });
    }

    function save_collectionrequest(){
        var collectionrequest_data = gather_collectionrequest_data();
        save_collectionrequest_data(collectionrequest_data);
    }

    function gather_collectionrequest_data(){
        var collectionrequest_data = {};

        collectionrequest_data['collectionrequest_details'] = get_collectionrequest_details();
        collectionrequest_data['microbe_collectionrequest_rows'] = get_microbe_collectionrequest_rows();
        collectionrequest_data['human_collectionrequest_rows'] = get_human_collectionrequest_rows();

        return collectionrequest_data;
    }

    function save_collectionrequest_data(collectionrequest_data){

        var final_data = JSON.stringify(collectionrequest_data);
        var path = window.location.href.split('/collection_requests')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_create_collection_requests',
            data: {'collection_requests_data': final_data},
            success: function (data) {
                window.location.href = data.url;
            },
            error: function (data) {
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

        var collectionrequest_details = {};

        collectionrequest_details['title'] = $("#title").val();
        collectionrequest_details['description'] = $("#description").val();
        collectionrequest_details['client'] = $("#Client_uid").val();
        collectionrequest_details['request_number'] = $("#RequestNumber").val();
        collectionrequest_details['date_of_request'] = $("#DateOfRequest").val();
        // collectionrequest_details['sample_kingdom'] = $("#SampleKingdom_uid").val();
        collectionrequest_details['collect_microbe_samples'] = $("#CollectMicrobeSamples").prop("checked");    //.val();
        collectionrequest_details['collect_human_samples'] = $("#CollectHumanSamples").prop("checked");                         //.val();
        collectionrequest_details['number_requested'] = $("#NumberRequested").val();

        // collectionrequest_details['date_evaluated'] = $("#DateEvaluated").val();
        // collectionrequest_details['result_of_evaluation'] = $("#ResultOfEvaluation").val();
        // collectionrequest_details['reason_for_evaluation'] = $("#ReasonForEvaluation").val();

        return collectionrequest_details;
    }

    function get_microbe_collectionrequest_rows(){
        var microbe_collectionrequests = [];
        $('.microbe-collectionrequest-rows').each(function(alqt_index, microbe_collectionrequest_row){
            var identification = $(microbe_collectionrequest_row).find('.microbe-collectionrequest-row-identification').val();
            var strain = $(microbe_collectionrequest_row).find('.microbe-collectionrequest-row-strain').val();
            var origin = $(microbe_collectionrequest_row).find('.microbe-collectionrequest-row-origin').val();
            var sample_type = $(microbe_collectionrequest_row).find('.microbe-collectionrequest-row-sample-type').val();
            var phenotype = $(microbe_collectionrequest_row).find('.microbe-collectionrequest-row-phenotype').val();
            // var storage_position = $(microbe_collectionrequest_row).find('.microbe-collectionrequest-row-').val();

            microbe_collectionrequests.push(
                {
                  'identification': identification,
                  'strain': strain,
                  'origin': origin,
                  'sample_type': sample_type,
                  'phenotype': phenotype,
                }
            );
        });
        return microbe_collectionrequests;
    }

    function get_human_collectionrequest_rows(){
        var human_collectionrequests = [];
        $('.human-collectionrequest-rows').each(function(alqt_index, human_collectionrequest_row){
            var barcode = $(human_collectionrequest_row).find('.human-collectionrequest-row-barcode').val();
            var sample_type = $(human_collectionrequest_row).find('.human-collectionrequest-row-sample-type').val();
            var sample_package = $(human_collectionrequest_row).find('.human-collectionrequest-row-sample-package').val();
            var volume = $(human_collectionrequest_row).find('.human-collectionrequest-row-volume').val();
            var unit = $(human_collectionrequest_row).find('.human-collectionrequest-row-unit').val();

            human_collectionrequests.push(
                {
                  'barcode': barcode,
                  'sample_type': sample_type,
                  'sample_package': sample_package,
                  'volume': volume,
                  'unit': unit,
                }
            );
        });
        return human_collectionrequests;
    }
}

function BaobabCollectionRequestGeneralView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('#contentActionMenus').remove();
    };
}


// function BaobabCollectionRequestView() {
//
//     var that = this;
//
//     that.load = function () {
//         // disable browser auto-complete
//         $('input[type=text]').prop('autocomplete', 'off');
//
//         hide_micro_organism_fields();
//
//         // $('#SampleKingdom_uid').focus(function() {
//         //     var uid = $('#SampleKingdom_uid').val();
//         //     toggle_micro_organism_fields(uid);
//         // });
//     };
//
//     function toggle_micro_organism_fields(sample_kingdom_uid){
//         var path = window.location.href.split('/collection_requests')[0] + '/is_micro_organism_kingdom';
//         $.ajax({
//             type: 'POST',
//             dataType: 'json',
//             url: path,
//             data: {'sample_kingdom_uid': sample_kingdom_uid}
//         }).success(function (data) {
//             if(data.is_micro_organism == true){
//                 display_micro_organism_fields();
//             }else{
//                 hide_micro_organism_fields();
//             };
//         })
//     }
//
//     // function display_micro_organism_fields(){
//     //     $('#archetypes-fieldname-Identificationz').show();
//     //     $('#archetypes-fieldname-Strain').show();
//     //     $('#archetypes-fieldname-OriginIsolatedFrom').show();
//     //     $('#archetypes-fieldname-Phenotype').show();
//     // }
//
//     function hide_micro_organism_fields(){
//         $('#archetypes-fieldname-MicrobeSampleRequests').hide();
//         $('#archetypes-fieldname-HumanSampleRequests').hide();
//     }
//
// }