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
        //debugger
        console.log('Salam');
    }

    function form_submit(){

    }
}