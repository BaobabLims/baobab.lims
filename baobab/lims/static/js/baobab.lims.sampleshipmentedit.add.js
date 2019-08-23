function BaobabSampleShipmentEditView() {

    var that = this;

    that.load = function () {
        $('#edit-bar').remove()

        $('#fieldsetlegend-default span').trigger("click")

        // $('#fieldsetlegend-delivery-info').css('background-color', '#ccc')
        // $('#fieldsetlegend-default').css('background-color', '#ccc')
        // $('#fieldsetlegend-correspondence').css('background-color', '#ccc')
        // $('#fieldsetlegend-shipping-information').css('background-color', '#ccc')

        $('#fieldsetlegend-default').click(function(){
            console.log('test default');
            $('#fieldsetlegend-default').css('background-color', '#ffffff')
            $('#fieldsetlegend-delivery-info').css('background-color', '#ccc')
            $('#fieldsetlegend-dates').css('background-color', '#ccc')
            $('#fieldsetlegend-correspondence').css('background-color', '#ccc')
            $('#fieldsetlegend-shipping-information').css('background-color', '#ccc')

            $('#fieldset-default').css('display', 'block');
            $('#fieldset-delivery-info').css('display', 'none');
            $('#fieldset-dates').css('display', 'none');
            $('#fieldset-correspondence').css('display', 'none');
            $('#fieldset-shipping-information').css('display', 'none');
        });

        $('#fieldsetlegend-delivery-info').click(function(){
            console.log('test delivery info');
            $('#fieldsetlegend-default').css('background-color', '#ccc')
            $('#fieldsetlegend-delivery-info').css('background-color', '#ffffff')
            $('#fieldsetlegend-dates').css('background-color', '#ccc')
            $('#fieldsetlegend-correspondence').css('background-color', '#ccc')
            $('#fieldsetlegend-shipping-information').css('background-color', '#ccc')

            $('#fieldset-default').css('display', 'none');
            $('#fieldset-delivery-info').css('display', 'block');
            $('#fieldset-dates').css('display', 'none');
            $('#fieldset-correspondence').css('display', 'none');
            $('#fieldset-shipping-information').css('display', 'none');
        });

        $('#fieldsetlegend-dates').click(function(){
            console.log('test dates');
            $('#fieldsetlegend-default').css('background-color', '#ccc')
            $('#fieldsetlegend-delivery-info').css('background-color', '#ccc')
            $('#fieldsetlegend-dates').css('background-color', '#ffffff')
            $('#fieldsetlegend-correspondence').css('background-color', '#ccc')
            $('#fieldsetlegend-shipping-information').css('background-color', '#ccc')

            $('#fieldset-default').css('display', 'none');
            $('#fieldset-delivery-info').css('display', 'none');
            $('#fieldset-dates').css('display', 'block');
            $('#fieldset-correspondence').css('display', 'none');
            $('#fieldset-shipping-information').css('display', 'none');
        });

        $('#fieldsetlegend-correspondence').click(function(){
            console.log('test correspondence');
            $('#fieldsetlegend-default').css('background-color', '#ccc')
            $('#fieldsetlegend-delivery-info').css('background-color', '#ccc')
            $('#fieldsetlegend-dates').css('background-color', '#ccc')
            $('#fieldsetlegend-correspondence').css('background-color', '#ffffff')
            $('#fieldsetlegend-shipping-information').css('background-color', '#ccc')

            $('#fieldset-default').css('display', 'none');
            $('#fieldset-delivery-info').css('display', 'none');
            $('#fieldset-dates').css('display', 'none');
            $('#fieldset-correspondence').css('display', 'block');
            $('#fieldset-shipping-information').css('display', 'none');
        });

        $('#fieldsetlegend-shipping-information').click(function(){
            console.log('test shipping information');
            $('#fieldsetlegend-default').css('background-color', '#ccc')
            $('#fieldsetlegend-delivery-info').css('background-color', '#ccc')
            $('#fieldsetlegend-dates').css('background-color', '#ccc')
            $('#fieldsetlegend-correspondence').css('background-color', '#ccc')
            $('#fieldsetlegend-shipping-information').css('background-color', '#ffffff')

            $('#fieldset-default').css('display', 'none');
            $('#fieldset-delivery-info').css('display', 'none');
            $('#fieldset-dates').css('display', 'none');
            $('#fieldset-correspondence').css('display', 'none');
            $('#fieldset-shipping-information').css('display', 'block');
        });

    };


}
