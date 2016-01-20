/**
 * Controller class for AnalysisRequest add view
 */
function CustomSupplyExAddView() {

    var that = this;

    // ------------------------------------------------------------------------
    // PUBLIC ACCESSORS
    // ------------------------------------------------------------------------


    // ------------------------------------------------------------------------
    // PUBLIC FUNCTIONS
    // ------------------------------------------------------------------------

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
                    window.bika.lims.portalWarningMessage('Number of kits you can assemble is: <strong>' + data + '</strong>', 'warning');
                }
            });
        });
    }

    function form_submit(){

    }
}