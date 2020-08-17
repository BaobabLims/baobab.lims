function BaobabReCulturingView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        setUpUI();
    };

    function setUpUI() {
        $('#archetypes-fieldname-NonConformities').hide();

        $('#Conformity').change(function () {
            if ($('#Conformity').val() == 'No') {
                $('#archetypes-fieldname-NonConformities').show();
            } else {
                $('#archetypes-fieldname-NonConformities').hide();
            }
        });
    }
}