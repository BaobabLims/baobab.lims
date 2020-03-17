function BaobabSamplePoolingView() {

    var that = this;

    that.load = function () {

        // $(':submit').remove();
        // $('.formControls').append('<button id="save_sample_pooling" class="context">Save Sample Pooling</button>');
        // // $('#archetypes-fieldname-InputSamples').remove()
        // // $('#archetypes-fieldname-ResultSamples').remove()
        //
        // $('#save_sample_pooling').click(function(event){
        //     event.preventDefault();
        //
        // });

        setUpUI();
    }

    function setUpUI(){
        //Remove the buttons and input and result textboxes
        $(':submit').remove();
        // $('.formControls').append('<button id="save_sample_pooling" class="context">Save Sample Pooling</button>');

        $('#archetypes-fieldname-InputSamples').remove();
        $('#archetypes-fieldname-ResultSamples').remove();

        //Add the Controls for the Pooling
        var input_samples = $('#fieldset-input-samples');

        //Add the section for selecting the samples to pool
        $(input_samples).append('<div class="div-input-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        $('.div-input-samples').append('<table class="tbl-input-samples"><thead class="head-input-samples"></thead><tbody class="body-input-samples"></tbody></table>');
        var input_sample_header_row = '\
            <tr>\
                <th>Aliquot Barcode</th>\
                <th>Volume</th>\
                <th>Unit</th>\
            </tr>\
        ';
        $('.head-input-samples').append(input_sample_header_row);
        $('.body-input-samples').append('<tr class="input-samples-rows"><td class="selected-input-sample"><td class="input-sample-volume"></td></td></tr>');

        $('.selected-input-sample').append('<select class="selected_sample" id="selected_sample_1"><option value=0>-- Select Input Sample --</option></select>');
        $('.input-sample-volume').append('<input type="text" class="selected-sample-volume" name="selected-sample-volume" />');
        get_samples('selected_sample_1');

        $('.div-input-samples').append('<div><button class="extra-input-samples">Another Input Sample</button></div>');

        $('.extra-input-samples').click(function(event){
            event.preventDefault();
            extra_input_samples();
        });

        //Add the section for creating new aliquots from this pooling
        $(input_samples).append('<div class="div-aliquot-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        $('.div-aliquot-samples').append('<table class="tbl-aliquot-samples"><thead class="head-aliquot-samples"></thead><tbody class="body-aliquot-samples"></tbody></table>');

        var aliquot_header_row = '\
            <tr>\
                <th>Aliquot Barcode</th>\
                <th>Volume</th>\
                <th>Unit</th>\
            </tr>\
        ';

        var aliquot_row = '\
            <tr class="aliquot-samples-rows" id="aliquot-samples-row-1">\
                <td><input type="text" class="aliquot-sample-barcode" id="aliquot-sample-barcode-1" /></td>\
                <td><input type="text" class="aliquot-sample-volume" id="aliquot-sample-volume-1" /></td>\
                <td><input type="text" class="aliquot-sample-unit" id="aliquot-sample-unit-1" /></td>\
            </tr>\
        ';

        // <td class="aliquot-sample-storage">
        //     <select class="aliquot-sample-storage" id="aliquot-sample-storage-1">
        //         <option value=0>-- Select Storage --</option>
        //     </select>
        // </td>

        $('.head-aliquot-samples').append(aliquot_header_row);
        $('.body-aliquot-samples').append(aliquot_row);

        $('.div-aliquot-samples').append('<div><button class="extra-aliquot-samples">Another Aliquot Sample</button></div>');

        $('.extra-aliquot-samples').click(function(event){
            event.preventDefault();
            extra_aliquot_samples();
        });


        //Add the new submit button and wire it up to the function that will save the new poolings
        $('.formControls').append('<button id="save_sample_pooling" class="context">Save Sample Pooling</button>');
        $('#save_sample_pooling').click(function(event){
            event.preventDefault();
            save_sample_pooling();
        });
    }

    function extra_input_samples(){

        // get the rows in this table
        var sample_rows = $('.input-samples-rows');
        var row_count = sample_rows.length + 1;
        var selected_sample_id = "input-sample-" + row_count;

        // create a new row
        var new_row = '\
            <tr  class="input-samples-rows">\
                <td><select class="selected_sample" id="' + selected_sample_id + '"><option value=0>-- Select Input Sample --</option></select></td> \
                <td><input type="text" class="selected-sample-volume" name="selected-sample-volume" /></td>\
            </tr>';

        // add it to the table
        $('.' + 'body-input-samples' + ' tr:last' ).after(new_row);
        get_samples(selected_sample_id);

    }

    function extra_aliquot_samples(){
        //

        // get the rows in this table
        var sample_rows = $('.aliquot-samples-rows');
        var row_count = sample_rows.length + 1;
        var aliquot_storage_id = "aliquot-storage-" + row_count;

        // create a new row
        var new_row = '\
            <tr  class="aliquot-samples-rows">\
                <td><input type="text"  class="aliquot-sample-barcode" id="aliquot-sample-barcode-' + row_count + '" /></td>\
                <td><input type="text"  class="aliquot-sample-volume" id="aliquot-sample-volume-' + row_count + '" /></td>\
                <td><input type="text"  class="aliquot-sample-unit" id="aliquot-sample-unit-' + row_count + '" /></td>\
            </tr>';

        // add it to the table
        $('.' + 'body-aliquot-samples' + ' tr:last' ).after(new_row);

        // get_samples(selected_sample_id);

    }

    function get_samples(select_id){
        var path = window.location.href.split('/sample_poolings')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             url: path + '/ajax_get_samples',
             success: function (data) {
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + select_id).append($('<option>').val(key).text(value));
                    });
                });
             }
         });
    }

     // function get_storages(select_id){
    //     var path = window.location.href.split('/sample_poolings')[0];
    //
    //      $.ajax({
    //          dataType: "json",
    //          contentType: 'application/json',
    //          url: path + '/ajax_get_storages',
    //          success: function (data) {
    //              $.each(data, function() {
    //                 $.each(this, function(key, value){
    //                     $('#' + select_id).append($('<option>').val(key).text(value));
    //                 });
    //             });
    //          }
    //      });
    // }

    function save_sample_pooling(){
        //
        var pooling_data = gather_pooling_data();
        // console.log('--------------');
        // console.log(pooling_data);

        var final_data = JSON.stringify(pooling_data);
        var path = window.location.href.split('/sample_poolings')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_create_poolings',
            data: {'pooling_data': final_data},
            success: function (data) {

                $("#success_message").css("display", "block");
                $("#success_message").find('.response_header').css("display", "block");
                $(".sample_group").remove();

                $.each(data, function(key, value) {
                    $("#success_list").append('<li class="response_li">' + value + '</li>');
                });

            },
            error: function (data) {
                $("#error_message").css("display", "block");
                $("#error_message").find('.response_header').css("display", "block");
                $(".sample_group").remove();
            },
        });

    }

    function gather_pooling_data(){
        var pooling_data = {};

        //get all the data for the new aliquots
        var sample_pooling_data = get_sample_pooling_data();
        var input_sample_data = get_input_samples_data();
        var aliquots_data = get_aliquots_data();

        pooling_data['sample_pooling_data'] = sample_pooling_data;
        pooling_data['input_samples_data'] = input_sample_data;
        pooling_data['aliquots_data'] = aliquots_data;

        // console.log('--------------');
        // console.log(aliquots_data);
        return pooling_data;
    }

    function get_sample_pooling_data(){

        var sample_pooling_data = {};

        sample_pooling_data['title'] = $("#title").val();
        sample_pooling_data['description'] = $("#description").val();
        sample_pooling_data['date_created'] = $("#DateCreated").val();
        sample_pooling_data['person_pooling'] = $("#PersonPooling").val();

        return sample_pooling_data;

    }

    function get_input_samples_data(){

       //extract the aliquots that are being created in this sample group
        var aliquots = [];
        $('.input-samples-rows').each(function(alqt_index, input_sample_row){
            console.log('=====');
            console.log(input_sample_row);
            var sample_uid = $(input_sample_row).find('.selected_sample').val();
            var volume = $(input_sample_row).find('.selected-sample-volume').val();
            // var unit = $(input_sample_row).find('.aliquot-sample-unit').val();
            // storage = $(aliquot_row).find('.storage').val();
            // datecreated = $(aliquot_row).find('.datecreated').val();
            // timecreated = $(aliquot_row).find('.timecreated').val();

            aliquots.push(
                {
                  'sample': sample_uid,
                  'volume': volume,
                  // 'unit': unit,
                  // 'storage': storage,
                  // 'datecreated': datecreated,
                  // 'timecreated': timecreated
                }
            );
        });

        return aliquots;
    }


    function get_aliquots_data(){

       //extract the aliquots that are being created in this sample group
        var aliquots = [];
        $('.aliquot-samples-rows').each(function(alqt_index, aliquot_row){
            console.log('=====');
            console.log(aliquot_row);
            var barcode = $(aliquot_row).find('.aliquot-sample-barcode').val();
            var volume = $(aliquot_row).find('.aliquot-sample-volume').val();
            var unit = $(aliquot_row).find('.aliquot-sample-unit').val();
            // storage = $(aliquot_row).find('.storage').val();
            // datecreated = $(aliquot_row).find('.datecreated').val();
            // timecreated = $(aliquot_row).find('.timecreated').val();

            aliquots.push(
                {
                  'barcode': barcode,
                  'volume': volume,
                  'unit': unit,
                  // 'storage': storage,
                  // 'datecreated': datecreated,
                  // 'timecreated': timecreated
                }
            );
        });

        return aliquots;
    }


    //
    // function clickReturnSample(){
    //     var yes_sample_uids = []
    //     var no_sample_uids = []
    //     var sample_shipment_uid = $('#sample_shipment_uid').val()
    //
    //     $('.will_sample_return').each(function(index, item){
    //         if (item.value == "yes"){
    //             yes_sample_uids.push(item.id)
    //         }
    //
    //         if (item.value == "no"){
    //             no_sample_uids.push(item.id)
    //         }
    //     });
    //
    //
    //     var path = window.location.href + '/setsamplesreturn';
    //     $.ajax({
    //         type: 'POST',
    //         dataType: 'json',
    //         url: path,
    //         data: {'sample_shipment_uid': sample_shipment_uid, 'yes_sample_uids': yes_sample_uids, 'no_sample_uids': no_sample_uids}
    //     }).always(function (data) {
    //         $('#workflow-transition-ready_shipment').removeClass('disable_hyperlink')
    //     })
    // }
    //
    // function setClientAddress(uid) {
    //     console.debug("uid is ", uid)
    //
    //     var requestData = {
    //         catalog_name: "portal_catalog",
    //         portal_type: "Client",
    //         UID: uid
    //     };
    //     window.bika.lims.jsonapi_read(requestData, function (data) {
    //         if (data.success && data.total_objects > 0) {
    //             physical_address = data.objects[0]['PhysicalAddress']
    //             billing_address = data.objects[0]['BillingAddress']
    //             //console.debug(data.objects[0])
    //
    //             physical_address = prepareAddress(physical_address)
    //             billing_address = prepareAddress(billing_address)
    //             if (!billing_address) {
    //                 billing_address = physical_address
    //             }
    //
    //             $('#DeliveryAddress').text(physical_address)
    //             $('#BillingAddress').text(physical_address)
    //         }
    //
    //     });
    //
    // }

}