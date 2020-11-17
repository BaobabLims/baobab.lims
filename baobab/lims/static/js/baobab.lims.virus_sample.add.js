function VirusSampleAddView(){
    var biospecFd = '#archetypes-fieldname-SampleType';
    var biospecSel = '#archetypes-fieldname-SampleType #SampleType';
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
    }

    function init() {
        // applyStyles();

        $('#archetypes-fieldname-LabHost').hide();
        $('#archetypes-fieldname-PassageNumber').hide();
        $('#archetypes-fieldname-PassageMethod').hide();

        $('#GeoLocCountry').change(function() {
            var geo_loc_country = this;
            var geo_loc_state = $('#GeoLocState');
            populate_dropdowns(geo_loc_state, 'states', {'country': geo_loc_country.value});
        });

        $('#archetypes-fieldname-InstrumentType').find('select').change(function() {
            var dropdown = this;
            var instrument = $('#archetypes-fieldname-Instrument').find('select');
            populate_dropdowns(instrument, 'instruments', {'selected_type': dropdown.value});
        });

        $('#SpecimenProcessing').change(function(e) {
            if ($(this).val() == "Virus Passage"){
                e.preventDefault();
                $('#archetypes-fieldname-LabHost').show();
                $('#archetypes-fieldname-PassageNumber').show();
                $('#archetypes-fieldname-PassageMethod').show();

            }else{
                e.preventDefault();
                $('#archetypes-fieldname-LabHost').hide();
                $('#archetypes-fieldname-PassageNumber').hide();
                $('#archetypes-fieldname-PassageMethod').hide();
            }
        });
    }

    function populate_dropdowns(dropdown, populate_type, data){
        var path = window.location.href.split('/virus_samples')[0];
        var url_path = path + '/ajax_get_' + populate_type;

         $.ajax({
             dataType: "json",
             contentType: 'application/json',
             data: data,
             url: url_path,
             success: function (data) {
                 $(dropdown).empty();
                 $.each(data, function() {
                    $.each(this, function(key, value){
                        $(dropdown).append($('<option>').val(key).text(value));
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

    // function populate_dropdowns(dropdown_id, populate_type, data){
    //     var path = window.location.href.split('/virus_samples')[0];
    //     var url_path = path + '/ajax_get_' + populate_type;
    //
    //      $.ajax({
    //          dataType: "json",
    //          contentType: 'application/json',
    //          data: data,
    //          url: url_path,
    //          success: function (data) {
    //              $('#' + dropdown_id).empty();
    //              $.each(data, function() {
    //                 $.each(this, function(key, value){
    //                     $('#' + dropdown_id).append($('<option>').val(key).text(value));
    //                 });
    //             });
    //          },
    //          error: function (jqXHR, textStatus, errorThrown) {
    //              console.log('This is the error');
    //              console.log(jqXHR);
    //              console.log(textStatus);
    //              console.log(errorThrown);
    //
    //          }
    //      });
    // }

    // function applyStyles() {
    //     $(biospecFd)
    //         .css('border', '1px solid #cfcfcf')
    //         .css('background-color', '#efefef')
    //         .css('padding', '10px')
    //         .css('margin-bottom', '20px');
    // }
}