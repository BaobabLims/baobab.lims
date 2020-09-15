function BaobabSamplePoolingView() {

    var that = this;

    that.load = function () {
        setUpUI();
    }

    function setUpUI(){
        removeExtraControls();

        //Add the Controls for the Pooling
        var input_samples = $('#fieldset-input-samples');

        var div_response_message = '\
        <div id="success_message" class="response_message" style="display: none;">\
            <h1 class="response_header">Sample pooling successfully created</h1>\
            <ul id="success_list" class="response_list">\
            </ul>\
        </div>\
        <div id="error_message" class="response_message" style="display: none;">\
            <h1 class="response_header" style="color: red;">Error when creating sample pooling</h1>\
            <ul id="error_list" class="response_list" style="color: red;">\
            </ul>\
        </div>\
        ';

        //Add the section for selecting the samples to pool
        $(input_samples).append(div_response_message);
        $(input_samples).append('<div class="div-input-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        $('.div-input-samples').append('<table class="tbl-input-samples"><thead class="head-input-samples"></thead><tbody class="body-input-samples"></tbody></table>');
        var input_sample_header_row = '\
            <tr>\
                <th>Aliquot Barcode</th>\
                <th>Taken Volume</th>\
                <th>Available Volume</th>\
            </tr>\
        ';
        $('.head-input-samples').append(input_sample_header_row);
        $('.body-input-samples').append('<tr class="input-samples-rows"><td class="selected-input-sample"><td class="input-sample-volume"><td id="input_available_volume_1" class="input-available-volume"></td></td></tr>');

        $('.selected-input-sample').append('<select class="selected_sample" id="selected_sample_1"><option value=0>-- Select Input Sample --</option></select>');
        $('.input-sample-volume').append('<input type="text" class="selected-sample-volume" name="selected-sample-volume" />');
        $('.input-available-volume').append('<input type="text" class="selected-available-volume" id="selected_available_volume_1" />');

        //set up the selected samples
        get_samples('selected_sample_1');
        $('#selected_sample_1').on('change', select_parent_sample);

        //at this spot call a function to set up the aliquot select

        $('.div-input-samples').append('<div><button class="extra-input-samples">Another Input Sample</button></div>');

        $('.extra-input-samples').click(function(event){
            event.preventDefault();
            extra_input_samples();
        });

        //Add a checkbox for adding an intermediate pooling sample
        buildIntermediateSampleUI(input_samples);

        //Add the section for creating new aliquots from this pooling
        $(input_samples).append('<div class="div-aliquot-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');

        $('.div-aliquot-samples').append('<div class="div-aliquot-storage-dropdowns"></div>');
        $('.div-aliquot-storage-dropdowns').append('<select class="aliquot-storage-unit"><option>-- Select Storage Unit --</option></select>');
        $('.div-aliquot-storage-dropdowns').append('<select class="aliquot-storage-box"><option>-- Select Box --</option></select>');
        $('.div-aliquot-samples').append('<table class="tbl-aliquot-samples"><thead class="head-aliquot-samples"></thead><tbody class="body-aliquot-samples"></tbody></table>');

        get_storage_units('aliquot-storage-unit');

        var aliquot_header_row = '\
            <tr>\
                <th>Aliquot Barcode</th>\
                <th>Volume</th>\
                <th>Unit</th>\
                <th>Sample Type</th>\
                <th>Project</th>\
                <th>Storage Position</th>\
            </tr>\
        ';

        var aliquot_row = '\
            <tr class="aliquot-samples-rows" id="aliquot-samples-row-1">\
                <td><input type="text" class="aliquot-sample-barcode" id="aliquot-sample-barcode-1" /></td>\
                <td><input type="text" class="aliquot-sample-volume" id="aliquot-sample-volume-1" /></td>\
                <td><input type="text" class="aliquot-sample-unit" id="aliquot-sample-unit-1" /></td>\
                <td><select class="aliquot-sample-sampletype" id="aliquot-sample-sampletype-1"><option value=0>-- Select Sample Type --</option></select></td>\
                <td><select class="aliquot-sample-project" id="aliquot-sample-project-1"><option value=0>-- Select Project --</option></select></td>\
                <td><select class="aliquot-sample-storageposition  storage" id="aliquot-sample-storageposition-1"><option value=0>-- Storage Position --</option></select></td>\
            </tr>\
        ';

        $('.head-aliquot-samples').append(aliquot_header_row);
        $('.body-aliquot-samples').append(aliquot_row);

        $('.aliquot-storage-unit').on('change', storage_unit_changed);
        $('.aliquot-storage-box').on('change', storage_box_changed);

        populate_dropdowns('aliquot-sample-sampletype-1', 'sampletypes');
        populate_dropdowns('aliquot-sample-project-1', 'projects');


        $('.div-aliquot-samples').append('<div><button class="extra-aliquot-samples">Another Aliquot Sample</button></div>');

        $('.extra-aliquot-samples').click(function(event){
            event.preventDefault();
            extra_aliquot_samples();
        });

        //Add the new submit button and wire it up to the function that will save the new poolings
        var buttons = '\
            <div class="savecancel_centrifugations_buttons">\
                <button id="save_sample_pooling" class="context">Save Sample Pooling</button>\
                <button class="cancel-centrifugation" name="form.button.cancel">Cancel</button>\
            </div>\
        ';
        $('.formControls').append(buttons);

        $('#save_sample_pooling').click(function(event){
            event.preventDefault();
            save_sample_pooling();
        });
    }

    function buildIntermediateSampleUI(input_samples){
        $(input_samples).append('<div class="div-intermediate-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        $('.div-intermediate-samples').append('<input type="checkbox" id="intermediate-pooling-sample" name="intermediate-pooling-sample" value="pool-intermediate-sample">');
        $('.div-intermediate-samples').append('<label for="intermediate-pooling-sample">Add an intermediate pooling sample</label>');

        $('.div-intermediate-samples').append('<div class="div-intermediate-storage-dropdowns"></div>');
        $('.div-intermediate-storage-dropdowns').append('<select class="intermediate-storage-unit"><option>-- Select Storage Unit --</option></select>');
        $('.div-intermediate-storage-dropdowns').append('<select class="intermediate-storage-box"><option>-- Select Box --</option></select>');

        get_storage_units('intermediate-storage-unit');

        $('.div-intermediate-samples').append('<table class="tbl-intermediate-samples"></table>');
        $('.tbl-intermediate-samples').append('<tr><th>Barcode</th><th>Volume</th><th>Unit</th><th>Sample Type</th><th>Project</th><th>Storage Position</th></tr>');
        var intermediate_row = '\
            <tr class="intermediate-sample-row" id="intermediate-sample-row">\
                <td><input type="text" class="intermediate-sample-barcode" id="intermediate-sample-barcode" /></td>\
                <td><input type="text" class="intermediate-sample-volume" id="intermediate-sample-volume" /></td>\
                <td><input type="text" class="intermediate-sample-unit" id="intermediate-sample-unit" /></td>\
                <td><select class="intermediate-sample-sampletype" id="intermediate-sample-sampletype"><option value=0>-- Select Sample Type --</option></select></td>\
                <td><select class="intermediate-sample-project" id="intermediate-sample-project"><option value=0>-- Select Project --</option></select></td>\
                <td><select class="intermediate-sample-storageposition storage" id="intermediate-sample-storageposition"><option value=0>-- Storage Position --</option></select></td>\
            </tr>\
        ';

        $('.tbl-intermediate-samples').append(intermediate_row);

        $('.intermediate-storage-unit').on('change', storage_unit_changed);
        $('.intermediate-storage-box').on('change', storage_box_changed);

        populate_dropdowns('intermediate-sample-sampletype', 'sampletypes');
        populate_dropdowns('intermediate-sample-project', 'projects');

        toggleDisplayIntermediateSample();
        $('.div-intermediate-storage-dropdowns').hide();
        $('.tbl-intermediate-samples').hide();

    }

    function toggleDisplayIntermediateSample(){
        $('#intermediate-pooling-sample').click(function(){
            if($(this).prop("checked") == true){
                $('.div-intermediate-storage-dropdowns').show();
                $('.tbl-intermediate-samples').show();
            }

            else if($(this).prop("checked") == false){
                $('.div-intermediate-storage-dropdowns').hide();
                $('.tbl-intermediate-samples').hide();
            }
        });
    }

    function removeExtraControls(){
        //Remove the buttons and input and result textboxes
        $('#samplepooling-base-edit').find(':submit').remove();
        // $('.formControls').append('<button id="save_sample_pooling" class="context">Save Sample Pooling</button>');

        $('#archetypes-fieldname-InputSamples').remove();
        $('#archetypes-fieldname-ResultSamples').remove();
    }

    function addSaveAndCancelButtons(div){
        var buttons = '\
            <div class="savecancel_centrifugations_buttons">\
                <button class="save-centrifugation">Save Centrifugation</button>\
                <button class="cancel-centrifugation" name="form.button.cancel">Cancel</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.save-centrifugation').click(function(event){
            event.preventDefault();
            save_centrifugation();
        });

        // $('.cancel-centrifugation').click(function(event){
        //     event.preventDefault();
        //     console.log('-------------------');
        //     console.log('Dummy cancel centrifugation');
        // });
    }

    function save_sample_pooling(){
        //
        var pooling_data = gather_pooling_data();
        console.log('--------------');
        console.log(pooling_data);

        var final_data = JSON.stringify(pooling_data);
        var path = window.location.href.split('/sample_poolings')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_create_poolings',
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

    function extra_input_samples(){

        // get the rows in this table
        var sample_rows = $('.input-samples-rows');
        var row_count = sample_rows.length + 1;
        var selected_sample_id = "selected_sample_" + row_count;
        var selected_available_volume_id = "selected_available_volume_" + row_count;


        // create a new row
        var new_row = '\
            <tr  class="input-samples-rows">\
                <td><select class="selected_sample" id="' + selected_sample_id + '"><option value=0>-- Select Input Sample --</option></select></td> \
                <td><input type="text" class="selected-sample-volume" name="selected-sample-volume" /></td>\
                <td><input type="text" class="selected-available-volume" id="' + selected_available_volume_id + '" /></td>\
            </tr>';

        // add it to the table
        $('.' + 'body-input-samples' + ' tr:last' ).after(new_row);
        get_samples(selected_sample_id);

    }

    function select_parent_sample(event){
        // get the sample group number from the id on the button
        var selected_sample = this;
        var id = selected_sample.id;
        var sample_uid = $(selected_sample).val();

        var sample_details_id = id.replace("selected_sample", "selected_available_volume");
        var sample_details = $('#' + sample_details_id);

        set_sample_details(sample_uid, sample_details);

    }

    function set_sample_details(sample_uid, sample_details){
        var path = window.location.href.split('/sample_poolings')[0];
        console.log('-----------Set sample details')
        console.log(sample_details)

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            data: { 'sample_uid': sample_uid },
            url: path + '/ajax_get_sample_details',
            success: function (data) {
                console.log('----success')
                console.log(data)
                // $(sample_details).html('<strong>' + data['volume'] + ' ' + data['unit'] + ' ' + data['storage'] + '</strong>');
                $(sample_details).val(data['volume'] + ' ' + data['unit'] + ' ' + data['storage']);
                $(sample_details).attr('title', data['volume'] + ' ' + data['unit'] + ' ' + data['storage']);

            },
            error: function(data){
                console.log('----error')
                $(sample_details).html();
                // console.log('------An error here');
                // console.log(data);

            },
        });
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
                <td><select class="aliquot-sample-sampletype" id="aliquot-sample-sampletype-' + row_count + '"><option value=0>-- Select Sample Type --</option></select></td>\
                <td><select class="aliquot-sample-project" id="aliquot-sample-project-' + row_count + '"><option value=0>-- Select Project --</option></select></td>\
                <td><select class="aliquot-sample-storageposition storage" id="aliquot-sample-storageposition-' + row_count + '"><option value=0>-- Storage Position --</option></select></td>\
            </tr>';

        // add it to the table
        $('.' + 'body-aliquot-samples' + ' tr:last' ).after(new_row);

        // get_samples(selected_sample_id);
        populate_dropdowns('aliquot-sample-project-' + row_count, 'projects');
        populate_dropdowns('aliquot-sample-sampletype-' + row_count, 'sampletypes');

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
        $('#' + select_id).on('change', select_parent_sample);
    }

    function populate_dropdowns(dropdown_id, populate_type){

        // console.log('===========Populate dropdowns');
        // console.log(dropdown_id);
        // console.log(populate_type);

        var path = window.location.href.split('/sample_poolings')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             url: path + '/ajax_get_' + populate_type,
             success: function (data) {
                 // console.log(data);
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + dropdown_id).append($('<option>').val(key).text(value));
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


    function gather_pooling_data(){
        var pooling_data = {};

        //get all the data for the new aliquots
        var sample_pooling_data = get_sample_pooling_data();
        var input_sample_data = get_input_samples_data();
        var aliquots_data = get_aliquots_data();
        var intermediate_sample_data =get_intermediate_sample_data();

        pooling_data['sample_pooling_data'] = sample_pooling_data;
        pooling_data['input_samples_data'] = input_sample_data;
        if($('#intermediate-pooling-sample').prop("checked") == true) {
            pooling_data['intermediate_sample_data'] = intermediate_sample_data;
        }
        pooling_data['aliquots_data'] = aliquots_data;

        // console.log('--------------Pooling Data');
        // console.log(pooling_data);
        return pooling_data;
    }

    function get_sample_pooling_data(){

        var sample_pooling_data = {};

        sample_pooling_data['title'] = $("#title").val();
        sample_pooling_data['description'] = $("#description").val();
        sample_pooling_data['date_created'] = $("#DateCreated").val();
        sample_pooling_data['analyst'] = $("#Analyst_uid").val();

        return sample_pooling_data;

    }

    function get_input_samples_data(){

       //extract the aliquots that are being created in this sample group
        var aliquots = [];
        $('.input-samples-rows').each(function(alqt_index, input_sample_row){
            // console.log('=====');
            // console.log(input_sample_row);
            var sample_uid = $(input_sample_row).find('.selected_sample').val();
            var volume = $(input_sample_row).find('.selected-sample-volume').val();
            var unit = $(input_sample_row).find('.aliquot-sample-unit').val();
            // storage = $(aliquot_row).find('.storage').val();
            // datecreated = $(aliquot_row).find('.datecreated').val();
            // timecreated = $(aliquot_row).find('.timecreated').val();

            aliquots.push(
                {
                  'sample': sample_uid,
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

    function get_intermediate_sample_data(){

        //extract the aliquots that are being created in this sample group
        var intermediate_sample_row = $('.intermediate-sample-row');

        var intermediate_barcode = $(intermediate_sample_row).find('.intermediate-sample-barcode').val();
        var intermediate_volume = $(intermediate_sample_row).find('.intermediate-sample-volume').val();
        var intermediate_unit = $(intermediate_sample_row).find('.intermediate-sample-unit').val();
        var intermediate_sampletype = $(intermediate_sample_row).find('.intermediate-sample-sampletype').val();
        var intermediate_project = $(intermediate_sample_row).find('.intermediate-sample-project').val();
        var intermediate_storage = $(intermediate_sample_row).find('.intermediate-sample-storageposition').val();

        return {
            'barcode': intermediate_barcode,
            'volume': intermediate_volume,
            'unit': intermediate_unit,
            'sampletype': intermediate_sampletype,
            'project': intermediate_project,
            'storage': intermediate_storage,
        }

    }

    function get_aliquots_data(){

       //extract the aliquots that are being created in this sample group
        var aliquots = [];
        $('.aliquot-samples-rows').each(function(alqt_index, aliquot_row){
            // console.log('=====');
            // console.log(aliquot_row);
            var barcode = $(aliquot_row).find('.aliquot-sample-barcode').val();
            var volume = $(aliquot_row).find('.aliquot-sample-volume').val();
            var unit = $(aliquot_row).find('.aliquot-sample-unit').val();
            var sampletype = $(aliquot_row).find('.aliquot-sample-sampletype').val();
            var project = $(aliquot_row).find('.aliquot-sample-project').val();
            var storage = $(aliquot_row).find('.storage').val();
            // datecreated = $(aliquot_row).find('.datecreated').val();
            // timecreated = $(aliquot_row).find('.timecreated').val();

            aliquots.push(
                {
                  'barcode': barcode,
                  'volume': volume,
                  'unit': unit,
                  'sampletype': sampletype,
                  'project': project,
                  'storage': storage,
                  // 'datecreated': datecreated,
                  // 'timecreated': timecreated
                }
            );
        });

        return aliquots;
    }

    function get_storage_units(select_class){
        var path = window.location.href.split('/sample_poolings')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             url: path + '/ajax_get_storage_units',
             success: function (data) {
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('.' + select_class).append($('<option>').val(key).text(value));
                    });
                });
             }
         });
    }

    function storage_unit_changed() {

        var storage_unit_class_pieces = this.className.split('-');
        var storage_box_class = storage_unit_class_pieces[0] + '-storage-box';

        var samples_table = 'tbl-' + storage_unit_class_pieces[0] + '-samples';
        var storages = $('.' + samples_table).find('.storage');

        set_boxes(this.value, storage_box_class);
        set_storage_positions(storages, this.value, 'StorageUnit');
    }

    function storage_box_changed() {

        var storage_box_class_pieces = this.className.split('-');

        var samples_table = 'tbl-' + storage_box_class_pieces[0] + '-samples';
        var storages = $('.' + samples_table).find('.storage');

        set_storage_positions(storages, this.value, 'ManagedStorage');
    }

    function set_boxes(storage_unit, storage_box_class){
        var path = window.location.href.split('/sample_poolings')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             data: {'storage_unit': storage_unit},
             url: path + '/ajax_get_boxes',
             success: function (data) {

                 $('.' + storage_box_class).empty();
                 $('.' + storage_box_class).append($('<option>').val(0).text('-- Select Storage --'));

                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('.' + storage_box_class).append($('<option>').val(key).text(value));
                    });
                });
             }
         });
    }

    function set_storage_positions(storages, storage_uid, storage_type) {

        var path = window.location.href.split('/sample_poolings')[0];

        $.ajax({
             dataType: "json",
             contentType: 'application/json',
             data: {'storage_uid': storage_uid, 'storage_type': storage_type},
             url: path + '/ajax_get_storage_positions',
             success: function (data) {

                 $.each(storages, function(idx, storage){
                     if($(storage).val() == 0) {
                         $(storage).empty();
                         $(storage).append($('<option>').val(0).text('-- Select Storage --'));

                         $.each(data, function () {
                             $.each(this, function (key, value) {
                                 $(storage).append($('<option>').val(key).text(value));
                             });
                         });
                     }
                 });
             }
         });
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