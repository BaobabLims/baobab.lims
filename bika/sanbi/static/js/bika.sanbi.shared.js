function ComputeKitTemplatePrice() {
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
    }
    function init(){
        productQuantityChanged()
    }

    function productQuantityChanged(){
        $("input.records_inputstring").on("click", function(event) {
            var inputID = $(this)[0].id;
            // console.log($(this))
        });
        /*var inputs = $(".ArchetypesRecordsWidget [combogrid_options]").not('.has_combogrid_widget');
        for (var i = inputs.length - 1; i >= 0; i--) {
            var element = inputs[i];
            var options = $.parseJSON($(element).attr('combogrid_options'));
            if(options == '' || options == undefined || options == null){
                continue;
            }
            options.select = function(event, ui){
                event.preventDefault();
                // Set value in activated element (must exist in colModel!)
                var fieldName = $(this).attr('name').split(".")[0];
                var key = "";
                if ($(this).attr('name').split(".").length > 1) {
                    key = $(this).attr('name').split(".")[1].split(":")[0];
                }
                console.log(key);
            }
        }*/

        $("#fieldsetlegend-price").on("click", function (e) {
            var productTitles = [];
            var productQuantities = [];
            var inputs = $(".ArchetypesRecordsWidget [combogrid_options]");
            for (var i = 0; i < inputs.length; i++) {
                var id = $(inputs[i])[0].id;
                var eType = id.split('-')[1];
                switch (eType){
                    case 'quantity':
                        if($(inputs[i]).val()){
                            productQuantities.push($(inputs[i]).val())
                        }else{
                            productQuantities.push("1");
                        }
                        break;
                    case 'product':
                        if($(inputs[i]).val()){
                            productTitles.push($(inputs[i]).val());
                        }
                        break;
                }
            }
            console.log(productQuantities);
            if(productTitles){
                var path = window.location.href.split('/edit')[0] + '/template_total_price';
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: path,
                    data: {'titles': productTitles}
                }).done(function (data) {
                    setPriceExcludingTVA(data, productTitles, productQuantities);
                })
            } 
        });

    }
    function setPriceExcludingTVA(data, titles, productQuantities){
        var totalPrice = 0;
        for(var i=0; i<data.length; i++){
            console.log(productQuantities[i]);
            totalPrice += parseFloat(data[i].price) * parseInt(productQuantities[i])
        }
        $("input#Price").val(totalPrice);
    }
}