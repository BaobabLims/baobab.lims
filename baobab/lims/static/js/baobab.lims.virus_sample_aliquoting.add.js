function VirusSampleAliquotAddView(){

    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        buildVirusSampleAliquot();
    }

    function buildVirusSampleAliquot(){
        var VSA = $('#fieldset-virus-sample-aliquot');

        $('#archetypes-fieldname-VirusAliquot').hide();
        addResponseMessage(VSA);
        addAliquotsFromSamplesGroupStructure(VSA);
        addVirusSampleAliquotSaveAndCancelButtons(VSA);
        displaySavedAliquots(VSA);
        // create_new_sample_group();
    }

    function addResponseMessage(VSA){
        var div_response_message = '\
        <div id="error_message" class="response_message" style="display: none;">\
            <h1 class="response_header" style="color: red;">Error when creating virus aliquots</h1>\
            <ul id="error_list" class="response_list" style="color: red;">\
            </ul>\
        </div>\
        ';

        $(VSA).append(div_response_message);
    }

    function displaySavedAliquots(VSA){
        $(VSA).prepend('<div class="div-saved-aliquots" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');
        var vga_data = get_viral_genomic_analysis_uid();
        buildSavedAliquotsDisplay(vga_data);
    }

    function get_viral_genomic_analysis_uid(){
        var virus_sample_aliquot_data = {};
        virus_sample_aliquot_data['viral_genomic_analysis_uid'] = $('#archetypes-fieldname-title').attr('data-uid');
        return virus_sample_aliquot_data;
    }

    function buildSavedAliquotsDisplay(vga_data){
        var final_data = JSON.stringify(vga_data);
        var path = window.location.href.split('/viral_genomic_analyses')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_retrieve_saved_aliquots',
            data: {'sample_aliquots': final_data},
            success: function (data) {

                $("#success_message").css("display", "block");
                $("#success_message").find('.response_header').css("display", "block");
                $(".sample_group").remove();

                var sample_count = 0;
                $.each(data, function(sample, saved_aliquots) {
                    sample_count = sample_count + 1;
                    var sample_table_id = 'body-aliquoted-sample-' + sample_count;
                    var aliquoted_sample_div_id = 'div-aliquoted-sample-' + sample_count;
                    $(".div-saved-aliquots").prepend('\
                        <div class="aliquoted_sample" style="border: solid; border-width: thin; margin: 10px; padding: 5px;">\
                            <h2>' + sample + '</h2>\
                            <table class="storage" style="border-collapse: collapse; width: 100%;">\
                                <thead>\
                                    <tr>\
                                        <th>Barcode</th>\
                                        <th>Volume</th>\
                                        <th>Unit</th>\
                                        <th>Sample Type</th>\
                                        <th>Date Created</th>\
                                    </tr>\
                                </thead>\
                                <tbody id=' + sample_table_id + '>\
                                </tbody>\
                            </table>\
                        </div>'
                    );

                    $.each(saved_aliquots, function(idx, aliquot){
                        var displayed_row = '\
                                <tr>\
                                    <td>' + aliquot.barcode + '</td>\
                                    <td>' + aliquot.volume + '</td>\
                                    <td>' + aliquot.unit + '</td>\
                                    <td>' + aliquot.sample_type + '</td>\
                                    <td>' + aliquot.date_created + '</td>\
                                </td>\
                            ';
                        $("#" + sample_table_id).append(displayed_row);
                    })
                });

                if (sample_count > 0){
                    $('.div-aliquot-from-sample').remove();
                    $('.savecancel_virus_sample_aliquot_buttons').remove();
                } else {
                    $('.div-saved-aliquots').remove();
                }
            },
            error: function (data) {
                $("#error_message").css("display", "block");
                $("#error_message").find('.response_header').css("display", "block");
            },
        });
    }

    function addAliquotsFromSamplesGroupStructure(VSA){
        $(VSA).append('<div class="div-aliquot-from-sample" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');

        $('.div-aliquot-from-sample').append('<div class="samples_and_aliquots_groups" style="margin: 0px; padding: 0px;"></div>');
        $('.div-aliquot-from-sample').append('<div id="buttons-group"></div>');
        $('#buttons-group').append('<button type="button" class="main_buttons" id="new_sample_group">New Sample Group</button>');
        $('#buttons-group').append('<button type="button" class="main_buttons" id="remove_last_sample_group">Remove Last Sample Group</button>');

        $('#new_sample_group').click(function(event){
            event.preventDefault();
            create_new_sample_group();
        });

        $('#remove_last_sample_group').click(function(event){
            event.preventDefault();
            $('.sample_group').last().remove();
        });
    }

    function addVirusSampleAliquotSaveAndCancelButtons(EGM){
        var div = $(EGM);
        var buttons = '\
            <div class="savecancel_virus_sample_aliquot_buttons">\
                <button type="button" class="save-virus-sample-aliquot">Save Aliquots</button>\
                <button class="cancel-virus-sample-aliquot" name="form.button.cancel">Cancel Aliquots</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.save-virus-sample-aliquot').click(function(event){
            event.preventDefault();
            var virus_sample_aliquot_data = get_virus_sample_aliquot_data();
            save_virus_sample_aliquot(virus_sample_aliquot_data);
        });

        $('.cancel-virus-sample-aliquot').click(function(event){
            event.preventDefault();
            var path = window.location.href.split('/edit')[0];
            window.location.href = path;
        });
    }

    function get_virus_sample_aliquot_data(){
        var virus_sample_aliquot_data = {};
        virus_sample_aliquot_data['viral_genomic_analysis_uid'] = $('#archetypes-fieldname-title').attr('data-uid');
        virus_sample_aliquot_data['sample_aliquot_rows'] = get_aliquot_rows_data();
        return virus_sample_aliquot_data;
    }

    function get_aliquot_rows_data(){
        var aliquots_data = {};

        // iterate all the sample groups and extract their values to be posted
        $('.sample_group').each(function(grp_index, sample_group){
            //extract the uid of the sample that was selected
            var select_value = $(sample_group).find('select').val();

            //extract the aliquots that are being created in this sample group
            var aliquots = [];
            $(sample_group).find('.aliquot_rows').each(function(alqt_index, aliquot_row){
                barcode = $(aliquot_row).find('.barcode').val();
                volume = $(aliquot_row).find('.volume').val();
                storage = $(aliquot_row).find('.storage').val();
                datecreated = $(aliquot_row).find('.datecreated').val();
                timecreated = $(aliquot_row).find('.timecreated').val();

                aliquots.push(
                    {
                      'barcode': barcode,
                      'volume': volume,
                      'storage': storage,
                      'datecreated': datecreated,
                      'timecreated': timecreated
                    }
                );
            });

            aliquots_data[select_value] = aliquots;
        });
        return aliquots_data;
    }

    function save_virus_sample_aliquot(virus_sample_aliquot_data){
        var final_data = JSON.stringify(virus_sample_aliquot_data);
        var path = window.location.href.split('/viral_genomic_analyses')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_create_virus_aliquots',
            data: {'sample_aliquots': final_data},
            success: function (data) {

                $("#success_message").css("display", "block");
                $("#success_message").find('.response_header').css("display", "block");
                $(".sample_group").remove();

                $.each(data, function(key, value) {
                    $("#success_list").append('<li class="response_li">' + value + '</li>');
                });

                window.location.href = data.url;

            },
            error: function (data) {
                // console.log('--------------the errors data');
                // console.log(data);
                // console.log(data.responseText);
                var error_response = JSON.parse(data.responseText);

                $("#error_message").css("display", "block");
                $("#error_message").find('.response_header').css("display", "block");
                $(".response_li").remove();
                error_response.error_message.forEach(function(item, index) {
                    $("#error_list").append('<li class="response_li" style="color: red;">' + item + '</li>');
                });
            },
        });
    }

    function create_new_sample_group(){
        var sample_groups = $('.sample_group');
        var next_sample_group = sample_groups.length + 1;
        create_sample_group_row(next_sample_group)
    }

    function create_sample_group_row(next_sample_group){
        var sample_group_div = '\
            <div class="sample_group" style="border: solid; border-width: thin; margin: 10px; padding: 5px;">\
                <div>\
                    <select id="sample_group_' + next_sample_group + '" class="sample_group_select">\
                        <option value="0">-- Select a sample to Aliquot --</option>\
                    </select>\
                    <span id="sample_details_' + next_sample_group + '"></span>\
                    <div>\
                        <select id="storage_unit_' + next_sample_group + '" class="storage_unit"><option>-- Select Storage Unit --</option></select>\
                        <select id="storage_box_' + next_sample_group + '" class="storage_box"><option>-- Select Box --</option></select>\
                    </div>\
                </div>\
                <div class="sample' + next_sample_group + '_aliquots">\
                    <table id="aliquots_table_' + next_sample_group + '">\
                        <tr>\
                            <th>Barcode<span style="color: red"> *</span></th>\
                            <th>Volume<span style="color: red"> *</span></th>\
                            <th>Date<span style="color: red"> *</span></th>\
                            <th>Time<span style="color: red"> *</span></th>\
                            <th>Storage</th>\
                        </tr>\
                        <tr class="aliquots_' + next_sample_group + '_rows aliquot_rows aliquots_' + next_sample_group + '_row_1">\
                            <td><input type="text" id="aliquots_' + next_sample_group + '_barcode_row_1" class="barcode" required></td>\
                            <td><input type="text" id="aliquots_' + next_sample_group + '_volume_row_1" class="volume" required></td>\
                            <td><input type="date" id="aliquots_' + next_sample_group + '_datecreated_row_1" class="datecreated" required></td>\
                            <td><input type="time" id="aliquots_' + next_sample_group + '_timecreated_row_1" class="timecreated" required></td>\
                            <td><select id="aliquots_' + next_sample_group + '_storage_row_1" class="storage"><option value=0>-- Select Storage --</option></select></td>\
                        </tr>\
                    </table>\
                </div>\
                <button class="one_more_aliquot" id="btn_sample_group_' + next_sample_group + '">One more aliquot</button>\
                <button class="remove_last_aliquot_row" id="btn_aliquot_remove_' + next_sample_group + '">Remove Last Row</button>\
            </div>';

        $('.samples_and_aliquots_groups').append(sample_group_div);
        $("#btn_sample_group_" + next_sample_group).on('click', add_aliquot_row);
        $("#btn_aliquot_remove_" + next_sample_group).on('click', remove_aliquot_row);
        $("#storage_unit_" + next_sample_group).on('change', storage_unit_changed);
        $("#storage_box_" + next_sample_group).on('change', storage_box_changed);
        $("#sample_group_" + next_sample_group).on('change', select_parent_sample);

        get_samples('sample_group_' + next_sample_group);
        get_storage_units('storage_unit_' + next_sample_group);

    }

    function get_samples(select_id){
        var path = window.location.href.split('/viral_genomic_analyses')[0];
        var project_uid = $('#Project_uid').val()

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            data: {'project_uid': project_uid},
            url: path + '/ajax_get_virus_samples',
            success: function (data) {
                $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + select_id).append($('<option>').val(key).text(value));
                    });
                });
            }
        });
    }

    function get_storage_units(select_id){
        var path = window.location.href.split('/viral_genomic_analyses')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             url: path + '/ajax_get_storage_units',
             success: function (data) {
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + select_id).append($('<option>').val(key).text(value));
                    });
                });
             }
         });
    }

    function remove_aliquot_row(){
        event.preventDefault();

        // get the sample group number from the id on the button
        var id = this.id;
        var sample_group = id.substring(19);

        // get the table
        var table_id = "aliquots_table_" + sample_group;

        $('#' + table_id + ' tr:last' ).remove();

    }

    function add_aliquot_row(event){
        event.preventDefault();
        // get the sample group number from the id on the button
        var id = this.id;
        var sample_group = id.substring(17);

        // get the table
        var table_id = "aliquots_table_" + sample_group;

        // get the rows in this table
        var aliquot_rows = $('.aliquots_' + sample_group + '_rows');
        var row_count = aliquot_rows.length + 1;

        // create a new row
        var new_row = '\
            <tr class="aliquots_' + sample_group + '_rows aliquot_rows">\
                <td><input type="text" id="aliquots_' + sample_group + '_barcode_row_' + row_count + '" class="barcode" required></td>\
                <td><input type="text" id="aliquots_' + sample_group + '_volume_row_' + row_count + '" class="volume" required></td> \
                <td><input type="date" id="aliquots_' + sample_group + '_datecreated_row_' + row_count + '" class="datecreated" required></td>\
                <td><input type="time" id="aliquots_' + sample_group + '_timecreated_row_' + row_count + '" class="timecreated" required></td>\
                <td><select id="aliquots_' + sample_group + '_storage_row_' + row_count + '" class="storage"><option value=0>-- Select Storage --</option></select></td> \
            </tr>\
            ';

        // add it to the table
        $('#' + table_id + ' tr:last' ).after(new_row);


    }

    function storage_unit_changed() {

        var sample_group_number = this.id.split('storage_unit_')[1];

        var aliquots_table_id = 'aliquots_table_' + sample_group_number;
        var aliquots_table = $('#' + aliquots_table_id);
        var storages = $(aliquots_table).find('.storage');

        set_boxes(this.value, 'storage_box_' + sample_group_number);
        set_storage_positions(storages, this.value, 'StorageUnit');
    }

    function set_boxes(storage_unit, storage_box_id){
        var path = window.location.href.split('/viral_genomic_analyses')[0];

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             data: {'storage_unit': storage_unit},
             url: path + '/ajax_get_boxes',
             success: function (data) {

                 $('#' + storage_box_id).empty();
                 $('#' + storage_box_id).append($('<option>').val(0).text('-- Select Storage --'));

                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $('#' + storage_box_id).append($('<option>').val(key).text(value));
                    });
                });
             }
         });
    }

    function set_storage_positions(storages, storage_uid, storage_type) {

        var path = window.location.href.split('/viral_genomic_analyses')[0];

        $.ajax({
             dataType: "json",
             contentType: 'application/json',
             data: {'storage_uid': storage_uid, 'storage_type': storage_type},
             url: path + '/ajax_get_storage_positions',
             success: function (data) {

                 $.each(storages, function(idx, storage){
                     $(storage).empty();
                     $(storage).append($('<option>').val(0).text('-- Select Storage --'));

                     $.each(data, function(){
                         $.each(this, function(key, value){
                            $(storage).append($('<option>').val(key).text(value));
                         });
                     });
                 });
             }
        });
    }

    function storage_box_changed() {

        var sample_group_number = this.id.split('storage_box_')[1];

        var aliquots_table_id = 'aliquots_table_' + sample_group_number;
        var aliquots_table = $('#' + aliquots_table_id);
        var storages = $(aliquots_table).find('.storage');

        // set_boxes(this.value, 'storage_box_' + sample_group_number);
        set_storage_positions(storages, this.value, 'ManagedStorage');
    }

    function select_parent_sample(event){
        // get the sample group number from the id on the button
        var selected_sample = this;
        var id = selected_sample.id;
        var sample_uid = $(selected_sample).val();

        var sample_details_id = id.replace("group", "details");
        var sample_details = $('#' + sample_details_id);

        set_sample_details(sample_uid, sample_details);

    }

    function set_sample_details(sample_uid, sample_details){
        var path = window.location.href.split('/viral_genomic_analyses')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            data: { 'sample_uid': sample_uid },
            url: path + '/ajax_get_sample_details',
            success: function (data) {
                $(sample_details).html('<strong>' + data['volume'] + ' ' + data['unit'] + ' ' + data['storage'] + '</strong>');

            },
            error: function(data){
                $(sample_details).html();
                // console.log('------An error here');
                // console.log(data);

            },
        });
    }

    // function create_aliquots(){
    //     $("#create_aliquots").on("click", function(e){
    //         var aliquots_data = get_aliquots_data();
    //         var final_data = JSON.stringify(aliquots_data);
    //         var path = window.location.href.split('/viral_genomic_analyses')[0];
    //
    //         $.ajax({
    //             dataType: "json",
    //             contentType: 'application/json',
    //             url: path + '/ajax_create_aliquots',
    //             data: {'sample_aliquots': final_data},
    //             success: function (data) {
    //
    //                 $("#success_message").css("display", "block");
    //                 $("#success_message").find('.response_header').css("display", "block");
    //                 $(".sample_group").remove();
    //
    //                 $.each(data, function(key, value) {
    //                     $("#success_list").append('<li class="response_li">' + value + '</li>');
    //                 });
    //
    //             },
    //             error: function (data) {
    //                 $("#error_message").css("display", "block");
    //                 $("#error_message").find('.response_header').css("display", "block");
    //                 $(".sample_group").remove();
    //             },
    //         });
    //
    //         e.preventDefault();
    //     });
    // }



    // function addTableHeader(table_header){
    //     var extract_table_header_row = '\
    //         <tr>\
    //             <th>Select Sample</th>\
    //             <th>Heat Inactivated</th>\
    //             <th>Method</th>\
    //             <th>New Sample Barcode</th>\
    //             <th>New Sample Volume</th>\
    //             <th>New Sample Unit</th>\
    //             <th>Kit Used</th>\
    //             <th>Kit Number</th>\
    //             <th>Notes</th>\
    //         </tr>\
    //     ';
    //
    //     $(table_header).append(extract_table_header_row);
    // }
    //
    // function appendTableRow(table_body){
    //     var extract_rows = $('.extract-rows');
    //     var row_count = extract_rows.length + 1;
    //     const first_row = 1;
    //
    //     var table_row = '\
    //       <tr class="extract-rows" id="extract_row_' + row_count + '">\
    //         <td><select class="extract-row-sample" id="extract_row_sample_' + row_count + '">\
    //             <option value=0>-- Select Sample --</option>\
    //         </select></td>\
    //         <td><input type="checkbox" class="extract-row-heat-inactivated" id="extract_row_heat_inactivated_' + row_count + '" ></td>\
    //         <td><select class="extract-row-method" id="extract_row_method_' + row_count + '">\
    //             <option value=0>-- Select Method --</option>\
    //         </select></td>\
    //         <td><input type="text" class="extract-row-newsamplebarcode" id="extract_row_newsamplebarcode' + row_count + '" ></td>\
    //         <td><input type="text" class="extract-row-newsamplevolume" id="extract_row_newsamplevolume_' + row_count + '" ></td>\
    //         <td><input type="text" class="extract-row-newsampleunit" id="extract_row_newsampleunit_' + row_count + '" ></td>\
    //         <td><input type="checkbox" class="extract-row-kitused" id="extract_row_kitused_' + row_count + '" ></td>\
    //         <td><input type="text" class="extract-row-kitnumber" id="extract_row_kitnumber_' + row_count + '" ></td>\
    //         <td><input type="text" class="extract-row-notes" id="extract_row_notes_' + row_count + '" ></td>\
    //       </tr>\
    //     ';
    //
    //
    //     if (row_count == first_row) {
    //         $(table_body).append(table_row);
    //     } else {
    //         $('.' + 'body-extract-genomic-material' + ' tr:last').after(table_row);
    //     }
    //
    //     populate_dropdowns('extract_row_sample_' + row_count, 'virus_samples');
    //     populate_dropdowns('extract_row_method_' + row_count, 'methods');
    //
    // }

    // function populate_dropdowns(dropdown_id, populate_type){
    //     var path = window.location.href.split('/viral_genomic_analyses')[0];
    //     var extract_data = {};
    //     extract_data['project_uid'] = $('#Project_uid').val()
    //
    //     $.ajax({
    //          dataType: "json",
    //          contentType: 'application/json',
    //          url: path + '/ajax_get_' + populate_type,
    //          data: extract_data,
    //          success: function (data) {
    //              $.each(data, function() {
    //                 $.each(this, function(key, value){
    //                     $('#' + dropdown_id).append($('<option>').val(key).text(value));
    //                 });
    //             });
    //          },
    //          error: function (data) {
    //             var error_response = JSON.parse(data.responseText);
    //
    //             $("#error_message").css("display", "block");
    //             $("#error_message").find('.response_header').css("display", "block");
    //             $(".response_li").remove();
    //             $("#error_list").append('<li class="response_li" style="color: red;">' + error_response.error_message + '</li>');
    //         },
    //     });
    // }
}