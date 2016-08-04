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