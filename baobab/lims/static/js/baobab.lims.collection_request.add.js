function BaobabCollectionRequestView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        hide_micro_organism_fields();

        $('#SampleKingdom_uid').focus(function() {
            var uid = $('#SampleKingdom_uid').val();
            toggle_micro_organism_fields(uid);
        });
    };

    function toggle_micro_organism_fields(sample_kingdom_uid){
        var path = window.location.href.split('/collection_requests')[0] + '/is_micro_organism_kingdom';
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: path,
            data: {'sample_kingdom_uid': sample_kingdom_uid}
        }).success(function (data) {
            if(data.is_micro_organism == true){
                display_micro_organism_fields();
            }else{
                hide_micro_organism_fields();
            };
        })
    }

    function display_micro_organism_fields(){
        $('#archetypes-fieldname-Identificationz').show();
        $('#archetypes-fieldname-Strain').show();
        $('#archetypes-fieldname-OriginIsolatedFrom').show();
        $('#archetypes-fieldname-Phenotype').show();

    }

    function hide_micro_organism_fields(){
        $('#archetypes-fieldname-Identificationz').hide();
        $('#archetypes-fieldname-Strain').hide();
        $('#archetypes-fieldname-OriginIsolatedFrom').hide();
        $('#archetypes-fieldname-Phenotype').hide();

    }

}