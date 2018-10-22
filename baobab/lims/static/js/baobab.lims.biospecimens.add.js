function BaobabBiospecimensView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        $($('select[selector^="Type_"]')).change(function () {
            cascadeSelectSampleType($(this))
        });
    }

    function cascadeSelectSampleType(selected_type){

        uid = selected_type.attr("uid");
        change_values = false;


        $('select[selector^="Type_"]').each(function( index, element ) {
            // console.debug(element.value)
            if (uid == $(element).attr('uid')){
                selected_value = $(element).val()
                change_values = true;
            }

            if (change_values == true){
                $(element).val(selected_value)
            }
        });
    }
}