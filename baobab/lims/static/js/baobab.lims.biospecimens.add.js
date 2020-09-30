function BiospecimensView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        setUpUI();
    };

    function setUpUI() {
        // console.log('This is a test');
        // alert('This is an alert');
        $('.item-listing-tbody > tr').each(function(){

            var row = $(this);
            var volume = $(row).find('.Volume');
            // console.log('---------------')
            // console.log(volume);
            var input = $(volume).find('input');

            if (parseFloat(input.val()) <= parseFloat('0.00')) {
                // console.log('This is ten');
                // alert('This is ten');
                $(row).css('border-bottom-color', 'red');
                $(row).css('border-width', 'medium');
                // var span = $(volume).find('.state-sample_received');
                // $(span).css('border-color', 'red');
            }
        })
    }
}