function BaobabSampleCentrifugationView() {

    var that = this;

    that.load = function () {
        console.log('Log add');
        setUpUI();
    }

    function setUpUI(){
        var centrifugations = $('#fieldset-centrifugations');
        removeControlsAndButton();
        addResponseMessage(centrifugations);
        addCentrifugationsTable(centrifugations);
        addSaveAndCancelButtons(centrifugations);
    }

    function removeControlsAndButton(){
        $('#centrifugation-base-edit').find(':submit').remove();
        $('#archetypes-fieldname-Centrifuges').remove();
    }

    function addResponseMessage(centrifugations){
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

        $(centrifugations).append(div_response_message);
    }

    function addCentrifugationsTable(centrifugations){
        $(centrifugations).append('<div class="div-centrifugation-samples" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');

        addTableStorageFilterDropdowns($('.div-centrifugation-samples'));
        $('.div-centrifugation-samples').append('<table class="tbl-centrifugation-samples"><thead class="head-centrifugation-samples"></thead><tbody class="body-centrifugation-samples"></tbody></table>');

        addTableHeader($('.head-centrifugation-samples'));
        appendTableRow($('.body-centrifugation-samples'));
        addTableRowManageButtons($('.div-centrifugation-samples'));
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

    function addTableStorageFilterDropdowns(div){
        $(div).append('<div class="div-centrifugation-storage-dropdowns"></div>');
        $('.div-centrifugation-storage-dropdowns').append('<select class="centrifugation-storage-unit"><option>-- Select Storage Unit --</option></select>');
        $('.div-centrifugation-storage-dropdowns').append('<select class="centrifugation-storage-box"><option>-- Select Box --</option></select>');

        get_storage_units('centrifugation-storage-unit');
        $('.centrifugation-storage-unit').on('change', storage_unit_changed);
        $('.centrifugation-storage-box').on('change', storage_box_changed);

    }

    function addTableHeader(table_header){
        var centrifugations_table_header_row = '\
            <tr>\
                <th>Condition</th>\
                <th>Sample Type</th>\
                <th>Volume</th>\
                <th>Unit</th>\
                <th>Barcode</th>\
                <th>Storage</th>\
            </tr>\
        ';

        $(table_header).append(centrifugations_table_header_row);
    }

    function appendTableRow(table_body){
        var centrifugation_rows = $('.centrifugation-rows');
        var row_count = centrifugation_rows.length + 1;
        const first_row = 1;

        var table_row = '\
            <tr class="centrifugation-rows" id="centrifugation_row_' + row_count + '">\
                <td><select class="centrifugation-row-condition" id="centrifugation_condition_' + row_count + '">\
                    <option value=0>-- Select Sample Condition --</option>\
                </select></td>\
                <td><select class="centrifugation-row-sample-type" id="centrifugation_sample_type_' + row_count + '">\
                    <option value=0>-- Select Sample Type --</option>\
                </select></td>\
                <td><input type="text" class="centrifugation-row-volume" id="centrifugation_volume_' + row_count + '" /></td>\
                <td><input type="text" class="centrifugation-row-unit" id="centrifugation_unit_' + row_count + '" /></td>\
                <td><input type="text" class="centrifugation-row-barcode" id="centrifugation_barcode_' + row_count + '" /></td>\
                <td><select class="centrifugation-row-storage-position storage" id="centrifugation_storage_position_' + row_count + '" id>\
                    <option value=0>-- Select Storage Position --</option>\
                </select></td>\
            </tr>\
        ';

        if (row_count == first_row) {
            $(table_body).append(table_row);
        } else {
            $('.' + 'body-centrifugation-samples' + ' tr:last').after(table_row);
        }
        populate_dropdowns('centrifugation_sample_type_' + row_count, 'sampletypes');
        populate_dropdowns('centrifugation_condition_' + row_count, 'sample_conditions');
    }

    function addTableRowManageButtons(div){

        var buttons = '\
            <div class="centrifugations_table_buttons">\
                <button class="extra-centrifuge-row">Add Centrifuge Row</button>\
                <button class="remove-last-centrifuge-row">Remove Last Row</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.extra-centrifuge-row').click(function(event){
            event.preventDefault();
            var table_body = $('.body-centrifugation-samples');
            appendTableRow(table_body);
        });

        $('.remove-last-centrifuge-row').click(function(event){
            event.preventDefault();
            $('.' + 'body-centrifugation-samples' + ' tr:last').remove();
        });
    }

    function populate_dropdowns(dropdown_id, populate_type){
        var path = window.location.href.split('/centrifugations')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             url: path + '/ajax_get_' + populate_type,
             success: function (data) {
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + dropdown_id).append($('<option>').val(key).text(value));
                    });
                });
             }
         });
    }

    function get_storage_units(select_class){
        var path = window.location.href.split('/centrifugations')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             url: path + '/ajax_get_storage_units',
             success: function (data) {
                 console.log(data);
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
        var path = window.location.href.split('/centrifugations')[0];

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

        var path = window.location.href.split('/centrifugations')[0];

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

    function save_centrifugation(){
        var centrifugation_data = gather_centrifugation_data();
        console.log('============centrifugation data');
        console.log(centrifugation_data);
        save_centrifugation_data(centrifugation_data);
    }

    function gather_centrifugation_data(){
        var centrifugation_data = {};

        centrifugation_data['centrifugation_details'] = get_centrifugation_details();
        centrifugation_data['centrifugation_rows'] = get_centrifugation_rows();

        return centrifugation_data;
    }

    function save_centrifugation_data(centrifugation_data){
        var final_data = JSON.stringify(centrifugation_data);
        var path = window.location.href.split('/centrifugations')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_create_centrifugations',
            data: {'centrifugation_data': final_data},
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


    function get_centrifugation_details(){

        var centrifugation_details = {};

        centrifugation_details['title'] = $("#title").val();
        centrifugation_details['description'] = $("#description").val();
        centrifugation_details['selectedsample'] = $("#SelectedSample_uid").val();
        centrifugation_details['date_created'] = $("#DateCreated").val();
        centrifugation_details['technician'] = $("#Technician_uid").val();
        centrifugation_details['technique'] = $("#Technique").val();

        return centrifugation_details;
    }

    function get_centrifugation_rows(){
        var centrifugations = [];
        $('.centrifugation-rows').each(function(alqt_index, centrifugation_row){
            var condition = $(centrifugation_row).find('.centrifugation-row-condition').val();
            var sampletype = $(centrifugation_row).find('.centrifugation-row-sample-type').val();
            var volume = $(centrifugation_row).find('.centrifugation-row-volume').val();
            var unit = $(centrifugation_row).find('.centrifugation-row-unit').val();
            var barcode = $(centrifugation_row).find('.centrifugation-row-barcode').val();
            var storage_position = $(centrifugation_row).find('.centrifugation-row-storage-position').val();

            centrifugations.push(
                {
                  'condition': condition,
                  'sampletype': sampletype,
                  'volume': volume,
                  'unit': unit,
                  'barcode': barcode,
                  'storageposition': storage_position,
                }
            );
        });
        return centrifugations;
    }
}