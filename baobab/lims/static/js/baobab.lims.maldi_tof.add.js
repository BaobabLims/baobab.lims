/**
 * Controller class for MALDI-TOF Add view
 */
function CustomMALDITOFAddView() {

    var that = this;
    var biobankNumFd = '#archetypes-fieldname-BioBankNumber';
    this.load = function() {
        init();
        ConditionalConformity()
    };

    function init() {
        applyStyles();
    }
    function ConditionalConformity(){
        $('#Conformity_1').click(function(event){
            $('#archetypes-fieldname-NonConformity').hide(); 
        });
        $('#Conformity_2').click(function(event){
            $('#archetypes-fieldname-NonConformity').show(); 
        });
    }
    function applyStyles() {
        /*$(biobankNumFd)
            .css('background', 'pink')*/
        $( ".required" ).css('float', 'none')
        $('.portaltype-malditof input[type=text]').css('width', '100px')
        $( "#archetypes-fieldname-BioBankNumber > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-BioBankNumber > label" ).insertAfter( $( "#archetypes-fieldname-BioBankNumber > .fieldErrorBox" ) );
        $( "#BioBankNumber_help" ).css('display', 'none')

        $( "#archetypes-fieldname-Strain > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-Strain > label" ).insertAfter( $( "#archetypes-fieldname-Strain > .fieldErrorBox" ) );
        $( "#Strain_help" ).css('display', 'none')

        $( "#archetypes-fieldname-DateOfMaldiTof > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-DateOfMaldiTof > label" ).insertAfter( $( "#archetypes-fieldname-DateOfMaldiTof > .fieldErrorBox" ) );
        $( "#DateOfMaldiTof_help" ).css('display', 'none')

        $( "#archetypes-fieldname-Result > label" ).css("padding-right","10px").css('margin-bottom', '20px')
        $( "#archetypes-fieldname-Result" ).css('margin-bottom', '50px')
        $( "#archetypes-fieldname-Result > label" ).insertAfter( $( "#archetypes-fieldname-Result > .fieldErrorBox" ) );
        $( "#Result_help" ).css('display', 'none')

        $( "#archetypes-fieldname-LevelOfConfidence" ).css("width","300px").css("float", "left")
        $( "#archetypes-fieldname-LevelOfConfidence > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-LevelOfConfidence > label" ).insertAfter( $( "#archetypes-fieldname-LevelOfConfidence > .fieldErrorBox" ) );
        $( "#LevelOfConfidence_help" ).css('display', 'none')

        $( "#archetypes-fieldname-Score > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-Score > label" ).insertAfter( $( "#archetypes-fieldname-Score > .fieldErrorBox" ) );
        $( "#Score_help" ).css('display', 'none')

        $( "#archetypes-fieldname-Score > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-Score > label" ).insertAfter( $( "#archetypes-fieldname-Score > .fieldErrorBox" ) );
        $( "#Score_help" ).css('display', 'none')

        $( "#archetypes-fieldname-Analyst > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-Analyst > label" ).insertAfter( $( "#archetypes-fieldname-Analyst > .fieldErrorBox" ) );
        $( "#Analyst_help" ).css('display', 'none')

        $( "#Conformity > div" ).css("font-weight","bold")
        $( "#Conformity > br" ).hide()


        $( "#archetypes-fieldname-NonConformity > label" ).css("padding-right","10px")
        $( "#archetypes-fieldname-NonConformity > label" ).insertAfter( $( "#archetypes-fieldname-NonConformity > .fieldErrorBox" ) );
        $( "#NonConformity_help" ).hide()
        $('#archetypes-fieldname-NonConformity').hide(); 
    }

}
