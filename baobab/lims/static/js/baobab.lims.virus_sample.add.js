function VirusSampleAddView(){
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

        $('#archetypes-fieldname-GeoLocCountry').change(function() {
            var geo_loc_country = $('#GeoLocCountry');
            var geo_loc_state = $('#GeoLocState');
            populate_dropdowns(geo_loc_state, 'states', {'country': geo_loc_country.val()});
        });

        $('#archetypes-fieldname-InstrumentType').find('select').change(function() {
            var dropdown = this;
            var instrument = $('#archetypes-fieldname-Instrument').find('select');
            populate_dropdowns(instrument, 'instruments', {'selected_type': dropdown.value});
        });

        $('#SpecimenProcessing').change(function(e) {
            if ($(this).val() == "Virus Passage"){
                $('#archetypes-fieldname-LabHost').show();
                $('#archetypes-fieldname-PassageNumber').show();
                $('#archetypes-fieldname-PassageMethod').show();

            }else{
                $('#archetypes-fieldname-LabHost').hide();
                $('#archetypes-fieldname-PassageNumber').hide();
                $('#archetypes-fieldname-PassageMethod').hide();
            }
        });
    }

    function populate_dropdowns(dropdown, populate_type, data){
        var url_path = portal_url + '/ajax_get_' + populate_type;

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

             }
         });
    }
}
