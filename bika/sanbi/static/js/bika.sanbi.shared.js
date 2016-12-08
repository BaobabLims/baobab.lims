function ComputeKitTemplatePrice() {
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
    };
    function init(){
        productQuantityChanged()
    }
    
    function productQuantityChanged(){
        $("input.records_inputstring").on("click", function(event) {
            var inputID = $(this)[0].id;
        });

        $("#fieldsetlegend-accounting").on("click", function (e) {
            var productUIDs = [];
            var productQuantities = [];
            var inputs = $(".ArchetypesRecordsWidget [combogrid_options]");
            var j = 0;
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
                            // productTitles.push($(inputs[i]).val());
                            productUIDs.push($('#ProductList-product_uid-' + j).val());
                        }
                        j++;
                        break;
                }
            }
            if(productUIDs){
                var path = window.location.href.split('/edit')[0] + '/template_total_price';
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: path,
                    data: {'uids': productUIDs}
                }).done(function (data) {
                    setPriceExcludingTVA(data, productQuantities);
                })
            } 
        });

    }
    function setPriceExcludingTVA(data, productQuantities){
        var totalPrice = 0;
        for(var i=0; i<data.length; i++){
            totalPrice += parseFloat(data[i].price) * parseInt(productQuantities[i])
        }
        $("input#Cost").val(totalPrice);
    }
}
