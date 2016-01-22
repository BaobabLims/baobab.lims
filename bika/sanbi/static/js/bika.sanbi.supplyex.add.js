/**
 * Controller class for AnalysisRequest add view
 */
function CustomSupplyExAddView() {

    var that = this;

    this.load = function() {

        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        doSomething()
        form_submit()

    };

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    function doSomething(){
        //debugger;
        $("#KitTemplate_uid").focus(function(){
            $.ajax({
                type: 'POST',
                url: window.location.href.replace("/edit", "") + "/computeNumberKits",
                data: {'KitTemplate': $('input[name="KitTemplate"]').val(), 'title': $(this).val(),
                       'catalog_name': $('input[name="KitTemplate"]').attr('catalog_name')},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if(data['error_msg']){
                        window.bika.lims.portalMessage(data['error_msg']);
                    }else{
                        window.bika.lims.portalWarningMessage('Number of kits you can assemble is: <strong>' + data['qtt'] + '</strong>', 'warning');
                    }
                }
            });
        });
    }

    function form_submit(){

        $('input[name="quantity"]').change(function(event){

        });

        $("#supplyex_edit").submit(function(event){
            var ok = true;
            if(!$('input[name="quantity"]').val() || $('input[name="quantity"]').val() == 0){
                window.bika.lims.portalMessage('Quantity should be specified');
                ok = false;
            }
            if (ok) {
                $.ajax({
                    type: 'POST',
                    url: window.location.href.replace("/edit", "") + "/updateStockItems",
                    data: {
                        'KitTemplate': $('input[name="KitTemplate"]').val(), 'title': $(this).val(),
                        'quantity': $('input[name="quantity"]').val(),
                        'catalog_name': $('input[name="KitTemplate"]').attr('catalog_name'),
                    },
                    dataType: "json",
                    async: false,
                    success: function (data, textStatus, $XHR) {
                        if (data['error_msg']) {
                            window.bika.lims.portalMessage(data['error_msg']);
                            ok = false;
                        } else {
                            window.bika.lims.portalInfoMessage(data['ok_msg']);
                        }
                    }
                });
            }
            if(! ok){
                event.preventDefault();
            }
        });
    }
}