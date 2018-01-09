function BaobabSampleShipmentView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        $('#Client_uid').focus(function() {
            var uid = $(this).val();
            var element = $("#DeliveryAddress");
            getClientAddress(element, uid);
        });

        $('input[type=submit]').on('click', function (event) {
            var path = window.location.href.split('/base_view')[0] + '/update_boxes';
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: {'locTitle': $('#StorageLocation').val()}
            }).done(function (data) {
                console.log(data);
            })
        })

    };

    function getClientAddress(element, filterValue) {
        $("#DeliveryAddress").text('test text here.');

    }
}