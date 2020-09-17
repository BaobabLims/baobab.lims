function BaobabCulturingView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        setUpUI();
    };

    function setUpUI() {

        $('#archetypes-fieldname-PolarFlagella').hide();
        $('#archetypes-fieldname-Lophotrichous').hide();
        $('#archetypes-fieldname-Peritrichous').hide();

        if ($('#Conformity').val() != 'No') {
            $('#archetypes-fieldname-NonConformities').hide();
        }

        $('#Conformity').change(function () {
            if ($('#Conformity').val() == 'No') {
                $('#archetypes-fieldname-NonConformities').show();
            } else {
                $('#archetypes-fieldname-NonConformities').hide();
            }
        });

        $('#Mobile').change(function () {
            if ($('#Mobile').val() == 'No') {
                $('#archetypes-fieldname-PolarFlagella').hide();
                $('#archetypes-fieldname-Lophotrichous').hide();
                $('#archetypes-fieldname-Peritrichous').hide();
            } else {
                $('#archetypes-fieldname-PolarFlagella').show();
                $('#archetypes-fieldname-Lophotrichous').show();
                $('#archetypes-fieldname-Peritrichous').show();
            }
        });
    }
}