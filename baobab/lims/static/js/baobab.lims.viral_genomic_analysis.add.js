function ViralGenomicAnalysisAddView(){
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        setUpUI();
    }

    function setUpUI() {
        console.log('------------The viral genomic analysis');
        removeExtraControls();
        buildExtractGenomicMaterial();
        // extractGenomicMaterial();
        // extractGenomicMaterial().buildExtractGenomicMaterial();

        addSaveAndCancelButtons();
    }

    function removeExtraControls(){
        //Remove the buttons and input and result textboxes
        $('#viralgenomicanalysis-base-edit').find(':submit').remove();

        $('#archetypes-fieldname-ExtractGenomicMaterial').remove();
    }

    function addSaveAndCancelButtons(){
        var div = $('.formControls');
        var buttons = '\
            <div class="savecancel_centrifugations_buttons">\
                <button type="button" class="save-viral-genomic-analysis">New Save Button</button>\
                <button class="cancel-centrifugation" name="form.button.cancel">New Cancel TODO:  Only remove save leave plone cancel button</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.save-viral-genomic-analysis').click(function(event){
            event.preventDefault();
            var viral_genomic_analysis_data = get_viral_genomic_analysis_data()
            save_viral_genomic_analysis(viral_genomic_analysis_data);
        });

    }

    function get_viral_genomic_analysis_data(){
        console.log('----------inside get data');
        var viral_genomic_analysis = {};

        viral_genomic_analysis['title'] = $('#title').val();
        viral_genomic_analysis['description'] = $('#description').val();
        viral_genomic_analysis['project'] = $('#Project_uid').val();
        viral_genomic_analysis['date_created'] = $('#DateCreated').val();
        viral_genomic_analysis['will_extract'] = $('#WillExtract').checked;
        viral_genomic_analysis['will_aliquot'] = $('#WillAliquot').checked;
        viral_genomic_analysis['will_quantify'] = $('#WillQuantify').checked;
        viral_genomic_analysis['will_viral_load_determine'] = $('#WillViralLoadDetermine').checked;
        viral_genomic_analysis['will_library_prep'] = $('#WillLibraryPrep').val();
        // viral_genomic_analysis[''] = $('#').val();

        return viral_genomic_analysis;
    }

    function save_viral_genomic_analysis(viral_genomic_analysis_data){
        var final_data = JSON.stringify(viral_genomic_analysis_data);
        var path = window.location.href.split('/viral_genomic_analyses')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_save_viral_genomic_analysis',
            data: {'viral_genomic_analysis': final_data},
            success: function (data) {
                console.log('--------------Successful.');
                console.log(data);
                console.log(data.url);
                // window.location.href = data.url;
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

    // function extractGenomicMaterial() {
        function buildExtractGenomicMaterial(){
            var EGM = $('#fieldset-extract-genomic-material');
            addExtractGenomicMaterialTable(EGM);
            addExtractGenomicMaterialSaveAndCancelButtons(EGM);

        }

        function addExtractGenomicMaterialTable(EGM){
            $(EGM).append('<div class="div-extract-genomic-material" style="border: solid; border-width: thin; margin: 10px; padding: 5px;"></div>');

            // addTableStorageFilterDropdowns($('.div-centrifugation-samples'));
            $('.div-extract-genomic-material').append('<table class="tbl-extract-genomic-material"><thead class="head-extract-genomic-material"></thead><tbody class="body-extract-genomic-material"></tbody></table>');

            addTableHeader($('.head-extract-genomic-material'));
            appendTableRow($('.body-extract-genomic-material'));
            addTableRowManageButtons($('.div-extract-genomic-material'));
        }

        function addExtractGenomicMaterialSaveAndCancelButtons(){
            var div = $('.formControls');
            var buttons = '\
                <div class="savecancel_extract_genomic_material_buttons">\
                    <button type="button" class="save-extract-genomic-material">Save Extract</button>\
                    <button class="cancel-centrifugation" name="form.button.cancel">Cancel Extract TODO:  Only remove save leave plone cancel button</button>\
                </div>\
            ';
            $(div).append(buttons);

            $('.save-extract-genomic-material').click(function(event){
                event.preventDefault();
                var extract_genomic_material_data = get_extract_genomic_material_data();
                save_extract_genomic_material(extract_genomic_material_data);
            });
        }

        function addTableHeader(table_header){
            var extract_table_header_row = '\
                <tr>\
                    <th>Select Sample</th>\
                    <th>Heat Inactivated</th>\
                    <th>Method</th>\
                    <th>New Sample Barcode</th>\
                    <th>New Sample Volume</th>\
                    <th>New Sample Unit</th>\
                    <th>Kit Used</th>\
                    <th>Kit Number</th>\
                    <th>Notes</th>\
                </tr>\
            ';

            $(table_header).append(extract_table_header_row);
        }

        function appendTableRow(table_body){
            var extract_rows = $('.extract-rows');
            var row_count = extract_rows.length + 1;
            const first_row = 1;

            var table_row = '\
              <tr class="extract-rows" id="extract_row_' + row_count + '">\
                <td><select class="extract-row-sample" id="extract_row_sample_' + row_count + '">\
                    <option value=0>-- Select Sample --</option>\
                </select></td>\
                <td><input type="checkbox" class="extract-row-heat-inactivated" id="extract_row_heat_inactivated_' + row_count + '" ></td>\
                <td><select class="extract-row-method" id="extract_row_method_' + row_count + '">\
                    <option value=0>-- Select Method --</option>\
                </select></td>\
                <td><input type="text" class="extract-row-newsamplebarcode" id="extract_row_newsamplebarcode' + row_count + '" ></td>\
                <td><input type="text" class="extract-row-newsamplevolume" id="extract_row_newsamplevolume_' + row_count + '" ></td>\
                <td><input type="text" class="extract-row-newsampleunit" id="extract_row_newsampleunit_' + row_count + '" ></td>\
                <td><input type="checkbox" class="extract-row-kitused" id="extract_row_kitused_' + row_count + '" ></td>\
                <td><input type="text" class="extract-row-kitnumber" id="extract_row_kitnumber_' + row_count + '" ></td>\
                <td><input type="text" class="extract-row-notes" id="extract_row_notes_' + row_count + '" ></td>\
              </tr>\
            ';


            if (row_count == first_row) {
                $(table_body).append(table_row);
            } else {
                $('.' + 'body-extract-genomic-material' + ' tr:last').after(table_row);
            }

            populate_dropdowns('extract_row_sample_' + row_count, 'virus_samples');
            populate_dropdowns('extract_row_method_' + row_count, 'methods');

        }

        function addTableRowManageButtons(div){

            var buttons = '\
                <div class="extract_table_buttons">\
                    <button class="extra-extract-row">Add Centrifuge Row</button>\
                    <button class="remove-last-extract-row">Remove Last Row</button>\
                </div>\
            ';
            $(div).append(buttons);

            $('.extra-extract-row').click(function(event){
                event.preventDefault();
                var table_body = $('.body-extract-genomic-material');
                appendTableRow(table_body);
            });

            $('.remove-last-extract-row').click(function(event){
                event.preventDefault();
                $('.' + 'body-extract-genomic-material' + ' tr:last').remove();
            });
        }

        function populate_dropdowns(dropdown_id, populate_type){
            var path = window.location.href.split('/viral_genomic_analyses')[0];
            var extract_data = {};
            extract_data['project_uid'] = $('#Project_uid').val()
            // var final_data = JSON.stringify(extract_data);
            // console.log(final_data);

             $.ajax({
                 dataType: "json",
                 contentType: 'application/json',
                 url: path + '/ajax_get_' + populate_type,
                 data: extract_data,
                 success: function (data) {
                     $.each(data, function() {
                        $.each(this, function(key, value){
                            $('#' + dropdown_id).append($('<option>').val(key).text(value));
                        });
                    });
                 },
                 error: function (data) {
                    var error_response = JSON.parse(data.responseText);

                    $("#error_message").css("display", "block");
                    $("#error_message").find('.response_header').css("display", "block");
                    $(".response_li").remove();
                    $("#error_list").append('<li class="response_li" style="color: red;">' + error_response.error_message + '</li>');
                },
             });
        }

        function get_extract_genomic_material_data(){
            var extract_genomic_material_data = {};
            extract_genomic_material_data['viral_genomic_analysis_uid'] = $('#archetypes-fieldname-title').attr('data-uid');
            extract_genomic_material_data['extract_genomic_material_rows'] = get_extract_genomic_material_rows_data();
            return extract_genomic_material_data;
        }

        function save_extract_genomic_material(extract_genomic_material_data){
            var final_data = JSON.stringify(extract_genomic_material_data);
            var path = window.location.href.split('/viral_genomic_analyses')[0];

            $.ajax({
                dataType: "json",
                contentType: 'application/json',
                url: path + '/ajax_save_extract_genomic_material',
                data: {'extract_genomic_material': final_data},
                success: function (data) {
                    // window.location.href = data.url;
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

        function get_extract_genomic_material_rows_data(){
            var extracts = [];
            $('.extract-rows').each(function(alqt_index, extract_row){
                var virus_sample = $(extract_row).find('.extract-row-sample').val();
                var heat_inactivated = $(extract_row).find('.extract-row-heat-inactivated').val();
                var method = $(extract_row).find('.extract-row-method').val();
                var new_sample_barcode = $(extract_row).find('.extract-row-newsamplebarcode').val();
                var new_sample_volume = $(extract_row).find('.extract-row-newsamplevolume').val();
                var new_sample_unit = $(extract_row).find('.extract-row-newsampleunit').val();
                var kit_used = $(extract_row).find('.extract-row-kitused').val();
                var kit_number = $(extract_row).find('.extract-row-kitnumber').val();
                var notes = $(extract_row).find('.extract-row-notes').val();

                extracts.push(
                    {
                      'virus_sample': virus_sample,
                      'heat_inactivated': heat_inactivated,
                      'method': method,
                      'new_sample_barcode': new_sample_barcode,
                      'new_sample_volume': new_sample_volume,
                      'new_sample_unit': new_sample_unit,
                      'kit_used': kit_used,
                      'kit_number': kit_number,
                      'notes': notes,
                    }
                );
            });
            return extracts;
        }

        // extractGenomicMaterial.buildExtractGenomicMaterial();
    // }
}

