/**
 * Controller class for kit add view
 */

function KitPrintView(){
    var that = this;

    this.load = function() {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');

        // Store referrer in cookie in case it is lost due to a page reload
        var backurl = document.referrer;
        if (backurl) {
            createCookie("ws.print.urlback", backurl);
        } else {
            backurl = readCookie("ws.print.urlback");
            if (!backurl) {
                backurl = portal_url;
            }
        }
        $('#print_button').click(function(e) {

            e.preventDefault();
            window.print();
        });

        $('#cancel_button').click(function(e) {
            e.preventDefault();
            location.href = backurl;
        });

        init();
    };

    function init() {
        loadBarcodes();
    }
    
    function loadBarcodes() {
        $('.barcode').each(function() {
            var id = $(this).attr('data-id');
            var code = $(this).attr('data-code');
            var barHeight = $(this).attr('data-barHeight');
            var addQuietZone = $(this).attr('data-addQuietZone');
            var showHRI = $(this).attr('data-showHRI');
            $(this).barcode(id, code,
                            {'barHeight': parseInt(barHeight),
                             'addQuietZone': Boolean(addQuietZone),
                             'showHRI': Boolean(showHRI) });
        });
    }
}

function CustomKitAddView() {
    var that = this;

    this.load = function() {
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
    };


    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------
    function listingProducts(products, currency, subtotal, vat, total){
        $("#productable").html(function(){
            var heading = "<table class='invoice-items items'> " +
                            "<thead> " +
                              "<tr>" +
                                "<th i18n:translate=''>Product</th>" +
                                "<th i18n:translate=''>Quantity</th>" +
                                "<th i18n:translate=''>Price</th>"
                              "</tr>" +
                            "</thead>" +
                            "<tbody>" ;
            var tbody = "";
            $.each(products, function(key, value){
                var tr = "<tr>" +
                           "<td tal:content='key'>"+ key  +"</td>" +
                           "<td class='number' tal:content='value[\'quantity\']'>"+ value['quantity'] +"</td>" +
                           "<td class='currency price' tal:content='value[\"price\"]'>"+ value['price'] +"</td>"
                         "</tr>"
                tbody += tr;
            });
            var trSubtotal = "<tr class='totals'>" +
                       "<td colspan='2' i18n:translate=''>Subtotal</td>" +
                       "<td class='currency'>" +
                         "<span>"+ currency +"</span>" +
                         "<span class='subtotal'>"+ subtotal +"</span>" +
                       "</td>" +
                      "</tr>";
            var trVAT = "<tr class='totals'>" +
                          "<td colspan='2' i18n:translate=''>VAT</td>" +
                          "<td class='currency'>" +
                            "<span>"+ currency +"</span>" +
                            "<span class='vat'>"+ vat +"</span>" +
                          "</td>" +
                        "</tr>";
            var trTotal = "<tr class='totals'>" +
                          "<td colspan='2' i18n:translate=''>Total</td>" +
                            "<td class='currency'>" +
                              "<span>"+ currency +"</span>" +
                              "<span class='vat'>"+ total +"</span>" +
                            "</td>" +
                          "</tr>";
            tbody = tbody + trSubtotal + trVAT + trTotal;

            return heading + tbody + "</tbody>" + "</table>";
        });
    }

    function init(){
        var path = window.location.href.split("/edit");
        $.ajax({
            type: 'POST',
            url: path[0] + "/objectExists",
            data:{},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                if(data['exist'] == true){
                    $("#KitTemplate_uid").trigger("focus");
                    console.log("done!");
                }
            }
        });
        numberKits();
        form_submit();
    }

    function setInfoFromKitTemplate(date, description) {
        if(! $("#expiryDate").val()){
            $("#expiryDate").val(date);
        }

        if(! $("#description").val()){
            $("#description").val(description);
        }
    }

    function numberKits(){
        //debugger;
        $("#KitTemplate_uid").on("focus", function(){
            var path = window.location.href.split("/edit")[0] + "/computeNumberKits";
            $.ajax({
                type: 'POST',
                url: path,
                data: {'KitTemplate': $('input[name="KitTemplate"]').val(), 'title': $(this).val(),
                       'catalog_name': $('input[name="KitTemplate"]').attr('catalog_name'),
                       'kit_quantity': $('input[name="quantity"]').val()},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if(data['error_msg']){
                        window.bika.lims.portalMessage(data['error_msg']);
                    }else{
                        window.bika.lims.portalWarningMessage('Number of kits you can assemble is: <strong>' + data['qtt'] + '</strong>', 'warning');
                        setInfoFromKitTemplate(data['expiry_date'], data['description']);
                        listingProducts(data['products'], data['currency'], data['subtotal'], data['vat'], data['total']);
                    }
                },
                error: function(){
                    console.log(path, arguments);
                }
            });
        });
    }

    function form_submit(){
        var ok = true;
        $('input[name="quantity"]').change(function(event){
            if(! ok) {
                ok = true;
            }
            if(! $('input[name="quantity"]').val() || $('input[name="quantity"]').val() == 0){
                window.bika.lims.portalMessage('Quantity should be specified');
                ok = false;
            }

            var path = window.location.href.split("/edit")[0] + "/computeNumberKits";
            $.ajax({
                type: 'POST',
                url: path,
                data: {'KitTemplate': $('input[name="KitTemplate"]').val(), 'title': $(this).val(),
                       'catalog_name': $('input[name="KitTemplate"]').attr('catalog_name'),
                       'kit_quantity': $('input[name="quantity"]').val()},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if(data['error_msg']){
                        window.bika.lims.portalMessage(data['error_msg']);
                    }else{
                        listingProducts(data['products'], data['currency'], data['subtotal'], data['vat'], data['total']);
                    }
                }
            });
        });

        $("#kitassembly_edit_form").submit(function(event){

            if(! $('#FormsThere').is(':checked')){
                window.bika.lims.portalMessage('Check Forms are joined to this kit.');
                ok = false;
            }else{
                ok = true;
            }
            if(! ok){
                event.preventDefault();
            }
        });
    }
}