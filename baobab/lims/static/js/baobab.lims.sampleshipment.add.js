function BaobabSampleShipmentView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        $('#Client_uid').focus(function() {
            var uid = $(this).val();

            setClientAddress(uid);
        });



    };

    function setClientAddress(uid){
        console.debug("uid is ", uid)

        var requestData = {
            catalog_name: "portal_catalog",
            portal_type: "Client",
            UID: uid
        };
        window.bika.lims.jsonapi_read(requestData, function (data) {
            if (data.success && data.total_objects > 0) {
                physical_address = data.objects[0]['PhysicalAddress']
                billing_address = data.objects[0]['BillingAddress']
                //console.debug(data.objects[0])

                physical_address = prepareAddress(physical_address)
                billing_address = prepareAddress(billing_address)
                if (!billing_address){
                    billing_address = physical_address
                }

                $('#DeliveryAddress').text(physical_address)
                $('#BillingAddress').text(physical_address)
            }

        });

    }

    function prepareAddress(address){
        var final_address = "";

        street_addess = address['address'];
        city = address['city'];
        state = address['state'];
        zip = address['zip'];
        country = address['country'];

        if (street_addess) {
            final_address = final_address.concat(street_addess.concat('\n'))
        }
        if (city) {
            final_address = final_address.concat(city.concat('\n'))
        }
        if (state) {
            final_address = final_address.concat(state.concat('\n'))
        }
        if (zip) {
            final_address = final_address.concat(zip.concat('\n'))
        }
        if (country) {
            final_address = final_address.concat(country.concat('\n'))
        }

        return final_address

    }

/*
    function getClientAddress(element, filterValue) {
        //do ajax here

        //this is not the right ajax.  just an example of how it can be done.
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

        //ajax will return data

        //

        $("#DeliveryAddress").text('test text here.');

    }
*/
}