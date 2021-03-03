function ViralGenomicAnalysisAddView(){
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        hideOtherTabs()
        // setUpUI();
    }

    function setUpUI() {
        removeExtraControls();
        addSaveAndCancelButtons();
    }
    function hideOtherTabs() {
        var processes = {'WillQuantify': 'genome-quantification',
                         'WillExtract': 'extract-genomic-material',
                         'WillAliquot': 'virus-sample-aliquot',
                         'WillViralLoadDetermine': 'viral-load-determination',
                         'WillLibraryPrep': 'sequencing-library-prep'}
        $.each(processes, function( key, value ) {
            if ($('#'+key).prop("checked")){
                $('#fieldsetlegend-'+value).show();
            }else{
                $('#fieldsetlegend-'+value).hide();
            }
        });
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

