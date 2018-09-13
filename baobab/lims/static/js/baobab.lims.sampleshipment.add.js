function BaobabSampleShipmentView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        $('#Client_uid').focus(function () {
            var uid = $(this).val();

            setClientAddress(uid);
        });

        var return_sample_timer = null
        $('.will_sample_return').change(function(event){
            $('#workflow-transition-ready_shipment').addClass('disable_hyperlink');
            if (return_sample_timer == null){
                return_sample_timer = setTimeout(clickReturnSample, 3500);
            }
            else{
                window.clearInterval(return_sample_timer);
                return_sample_timer = null;
                return_sample_timer = setTimeout(clickReturnSample, 3500);
            }
        });
    }

    function clickReturnSample(){
        var yes_sample_uids = []
        var no_sample_uids = []
        var sample_shipment_uid = $('#sample_shipment_uid').val()

        $('.will_sample_return').each(function(index, item){
            if (item.value == "yes"){
                yes_sample_uids.push(item.id)
            }

            if (item.value == "no"){
                no_sample_uids.push(item.id)
            }
        });


        var path = window.location.href + '/setsamplesreturn';
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: path,
            data: {'sample_shipment_uid': sample_shipment_uid, 'yes_sample_uids': yes_sample_uids, 'no_sample_uids': no_sample_uids}
        }).always(function (data) {
            $('#workflow-transition-ready_shipment').removeClass('disable_hyperlink')
        })
    }

    function setClientAddress(uid) {
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
                if (!billing_address) {
                    billing_address = physical_address
                }

                $('#DeliveryAddress').text(physical_address)
                $('#BillingAddress').text(physical_address)
            }

        });

    }

    function prepareAddress(address) {
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
}