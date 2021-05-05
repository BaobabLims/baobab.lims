function ViralGenomicAnalysisAddView(){
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        // hideOtherTabs()
        // setUpUI();

        displayTabs();
        $('#ReferenceSampleControlResult').change(function(e) {
            if ($(this).val() == "Fail"){
                $('#archetypes-fieldname-ViralLoadDetermination').hide();

            }else{
                $('#archetypes-fieldname-ViralLoadDetermination').show();
            }
        });
    }

    function setUpUI() {
        removeExtraControls();
        addSaveAndCancelButtons();
    }

    // function hideOtherTabs() {
    //     var processes = {'WillQuantify': 'genome-quantification',
    //                      'WillExtract': 'extract-genomic-material',
    //                      'WillAliquot': 'virus-sample-aliquot',
    //                      'WillViralLoadDetermine': 'viral-load-determination',
    //                      'WillLibraryPrep': 'sequencing-library-prep'}
    //     $.each(processes, function( key, value ) {
    //         if ($('#'+key).prop("checked")){
    //             $('#fieldsetlegend-'+value).show();
    //         }else{
    //             $('#fieldsetlegend-'+value).hide();
    //         }
    //     });
    // }

    function displayTabs(){
        hideAllTabs();
        displayAppropriateTabs();
        displayOrHideSaveAndCancelButtons();

    }

    function displayOrHideSaveAndCancelButtons(){
        $('.formTab').click(function(event){
            console.log('-----------Am I raising this');
            if($('#fieldset-virus-sample-aliquot').css('display') == 'none'){
                console.log('------------Is visible')
                $(":submit").show();
            } else {
                console.log('------------Not seen')
                $(":submit").hide();
            }
        })
    }

    function hideAllTabs(){
        $('#fieldsetlegend-genome-quantification').hide()
        $('#fieldsetlegend-extract-genomic-material').hide()
        $('#fieldsetlegend-virus-sample-aliquot').hide()
        $('#fieldsetlegend-viral-load-determination').hide()
        $('#fieldsetlegend-sequencing-library-prep').hide()

    }

    function displayAppropriateTabs(){
        var vga_info = get_vga_info()
        var final_data = JSON.stringify(vga_info);
        var path = window.location.href.split('/viral_genomic_analyses')[0];

        $.ajax({
            dataType: "json",
            contentType: 'application/json',
            url: path + '/ajax_retrieve_tab_display_info',
            data: {'vga_info': final_data},
            success: function (data) {
                console.log('----------tab display info');
                console.log(data);
                console.log(data.vga_will_extract);
                console.log(data.vga_will_aliquot);
                console.log(data.vga_will_quantify);
                console.log(data.vga_status);

                if (data.vga_will_quantify== true)
                    $('#fieldsetlegend-genome-quantification').show()

                if (data.vga_will_extract == true)
                    $('#fieldsetlegend-extract-genomic-material').show()

                if (data.vga_will_aliquot == true)
                    $('#fieldsetlegend-virus-sample-aliquot').show()

                if (data.vga_will_viral_load_determine == true)
                    $('#fieldsetlegend-viral-load-determination').show()

                if (data.vga_will_library_prep == true)
                    $('#fieldsetlegend-sequencing-library-prep').show()

                // if (data.vga_status != 'aliquoted' && data.vga_status != 'genome_quantified') {
                //     $('.save-virus-sample-aliquot').hide()
                //     $('.cancel-virus-sample-aliquot').hide()
                // }


                // if (data.vga_status == 'created'){
                //     $('#fieldsetlegend-virus-sample-aliquot button').hide()
                //     $('#fieldsetlegend-genome-quantification submit').hide()
                //     $('#fieldsetlegend-viral-load-determination submit').hide()
                //     $('#fieldsetlegend-sequencing-library-prep submit').hide()
                // }
                //
                // if (data.vga_status == 'extracted_genomic_material'){
                //     $('#fieldsetlegend-virus-sample-aliquot button').hide()
                //     $('#fieldsetlegend-genome-quantification submit').hide()
                //     $('#fieldsetlegend-viral-load-determination submit').hide()
                //     $('#fieldsetlegend-sequencing-library-prep submit').hide()
                // }
                //
                // if (data.vga_status == 'aliquoted'){
                //     $('#fieldsetlegend-extract-genomic-material submit').hide()
                //     // $('#fieldsetlegend-virus-sample-aliquot button').hide()
                //     // $('#fieldsetlegend-genome-quantification submit').hide()
                //     $('#fieldsetlegend-viral-load-determination submit').hide()
                //     $('#fieldsetlegend-sequencing-library-prep submit').hide()
                // }
                //
                // if (data.vga_status == 'genome_quantified'){
                //     $('#fieldsetlegend-genome-quantification submit').hide()
                //     $('#fieldsetlegend-extract-genomic-material submit').hide()
                //     // $('#fieldsetlegend-virus-sample-aliquot button').hide()
                //     // $('#fieldsetlegend-viral-load-determination submit').hide()
                //     $('#fieldsetlegend-sequencing-library-prep submit').hide()
                // }
                //
                // if (data.vga_status == 'viral_load_determined'){
                //     $('#fieldsetlegend-genome-quantification submit').hide()
                //     $('#fieldsetlegend-extract-genomic-material submit').hide()
                //     $('#fieldsetlegend-virus-sample-aliquot button').hide()
                //     // $('#fieldsetlegend-viral-load-determination submit').hide()
                //     // $('#fieldsetlegend-sequencing-library-prep submit').hide()
                // }
                //
                // if (data.vga_status == 'sequencing_library_preped'){
                //     $('#fieldsetlegend-genome-quantification submit').hide()
                //     $('#fieldsetlegend-extract-genomic-material submit').hide()
                //     $('#fieldsetlegend-virus-sample-aliquot submit').hide()
                //     $('#fieldsetlegend-viral-load-determination submit').hide()
                //     // $('#fieldsetlegend-sequencing-library-prep submit').hide()
                // }

            },
            error: function (data) {
                // $("#error_message").css("display", "block");
                // $("#error_message").find('.response_header').css("display", "block");
                $('#fieldsetlegend-genome-quantification').show()
                $('#fieldsetlegend-extract-genomic-material').show()
                $('#fieldsetlegend-virus-sample-aliquot').show()
                $('#fieldsetlegend-viral-load-determination').show()
                $('#fieldsetlegend-sequencing-library-prep').show()
            },
        });
    }

    function get_vga_info(){
        var vga_info = {};
        vga_info['viral_genomic_analysis_uid'] = $('#archetypes-fieldname-title').attr('data-uid');
        return vga_info;
    }

    function removeExtraControls(){
        //Remove the buttons and input and result textboxes
        $('#viralgenomicanalysis-base-edit').find(':submit').remove();
    }

    function addSaveAndCancelButtons(){
        var div = $('#fieldset-default');
        var buttons = '\
            <div class="savecancel_centrifugations_buttons" style="margin: 4pt;">\
                <button type="button" class="save-viral-genomic-analysis">Save Viral Genomic Analysis</button>\
                <button class="cancel-viral-genomic-analysis" name="form.button.cancel">Cancel</button>\
            </div>\
        ';
        $(div).append(buttons);

        $('.save-viral-genomic-analysis').click(function(event){
            event.preventDefault();
            var viral_genomic_analysis_data = get_viral_genomic_analysis_data()
            save_viral_genomic_analysis(viral_genomic_analysis_data);
        });

        $('.cancel-viral-genomic-analysis').click(function(event){
            event.preventDefault();
            var path = window.location.href.split('/edit')[0];
            window.location.href = path;
        });

    }

    function get_viral_genomic_analysis_data(){
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
                window.location.href = data.url;
            },
            error: function (data) {
                var error_response = JSON.parse(data.responseText);

                $("#error_message").css("display", "block");
                $("#error_message").find('.response_header').css("display", "block");
                $(".response_li").remove();
                $("#error_list").append('<li class="response_li" style="color: red;">' + error_response.error_message + '</li>');
                // alert(error_response.error_message);
            },
        });
    }
}

