function BaobabBiospecimensView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        // SampleBatch Add/Edit page: hide or show the colour of Plasma/Serum based on selected batch type
        // $('tr[fieldname=SerumColour]').hide();
        updateSerumColour();

        $('#BatchType').change(function() {
            updateSerumColour();
        });

        $($('select[selector^="Type_"]')).change(function () {
            cascadeSelectSampleType($(this))
        });

        $($('input[selector^="Barcode_"]')).on('input', function() {                //change(function () {
            var barcode_change_timer = null
            if (barcode_change_timer == null){
                uid = $(this).attr('uid')
                barcode_change_timer = setTimeout(function(){updateFrozenTime(uid)}, 500);
            }
            else{
                window.clearInterval(barcode_change_timer);
                barcode_change_timer = null;
                barcode_change_timer = setTimeout(function(){updateFrozenTime(uid)}, 500);
            }
        });
    }

    function updateSerumColour() {
        var batchTypeSelected = $("#BatchType :selected").text().toLowerCase();
        var regex = new RegExp('(plasma|serum)');
        if (regex.test(batchTypeSelected)) {
            $('tr[fieldname=SerumColour]').show();
        } else {
            $('tr[fieldname=SerumColour]').hide();
            $('#SerumColour option:first-child').attr("selected", "selected");
        }
    }

    function updateFrozenTime(uid){

        $('input[selector^="Barcode_"]').each(function( index, element ) {
            if (uid == $(element).attr('uid')){

                var d = new Date();
                current_date = [
                  d.getFullYear(),
                  ('0' + (d.getMonth() + 1)).slice(-2),
                  ('0' + d.getDate()).slice(-2)
                ].join('-');

                current_time = [
                    d.getHours(),
                    ('0' + d.getMinutes()).slice(-2)
                ].join(':');

                current_date_and_time = current_date + ' ' + current_time

                $('input[selector^="FrozenTime_"]').each(function( frozen_index, frozen_element ) {
                    $(frozen_element).val(current_date_and_time)

                    //if (index == frozen_index){
                    //    console.debug(frozen_element)
                    //    $(frozen_element).val(current_date_and_time)
                    //}
                });

            }
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
