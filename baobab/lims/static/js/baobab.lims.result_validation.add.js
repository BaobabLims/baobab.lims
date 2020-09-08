/**
 * Controller class for MALDI-TOF Add view
 */
function CustomResultVerifiationAddView() {

    var that = this;
    var biobankNumFd = '#archetypes-fieldname-BioBankNumber';
    this.load = function() {
        init();
        ConditionalStrainValidation()
        ConditionalDeliveryOfCerticate()
        ConditionalBiobankedStorage()
    };

    function init() {
        applyStyles();
    }
    function ConditionalStrainValidation(){
        $('#StrainValidation_2').click(function(event){
            $('#archetypes-fieldname-DateOfValidation').hide(); 
        });
        $('#StrainValidation_1').click(function(event){
            $('#archetypes-fieldname-DateOfValidation').show(); 
        });
    }
    function ConditionalDeliveryOfCerticate(){
        $('#DeliveryOfCerticate_2').click(function(event){
            $('#archetypes-fieldname-DateDelivered').hide(); 
        });
        $('#DeliveryOfCerticate_1').click(function(event){
            $('#archetypes-fieldname-DateDelivered').show(); 
        });
    }
    function ConditionalBiobankedStorage(){
        $('#BiobankedStorage_2').click(function(event){
            $('#archetypes-fieldname-DateStored').hide(); 
        });
        $('#BiobankedStorage_1').click(function(event){
            $('#archetypes-fieldname-DateStored').show(); 
        });
    }
    function applyStyles() {
        /*$(biobankNumFd)
            .css('background', 'pink')*/
        $("#archetypes-fieldname-title > label" ).css("padding-right","10px")
        $("#archetypes-fieldname-title > label" ).insertAfter( $( "#archetypes-fieldname-title > .fieldErrorBox" ) );
        $("#BioBankNumber_help" ).css('display', 'none')

        $("#StrainValidation_help" ).css('display', 'none')
        $("#StrainValidation > div" ).css("font-weight","bold")
        $("#StrainValidation > br" ).hide()
        $('#archetypes-fieldname-DateOfValidation').hide(); 

        $("#DeliveryOfCerticate_help" ).css('display', 'none')
        $("#DeliveryOfCerticate > div" ).css("font-weight","bold")
        $("#DeliveryOfCerticate > br" ).hide()
        $('#archetypes-fieldname-DateDelivered').hide(); 

        $("#BiobankedStorage_help" ).css('display', 'none')
        $("#BiobankedStorage > div" ).css("font-weight","bold")
        $("#BiobankedStorage > br" ).hide()
        $('#archetypes-fieldname-DateStored').hide(); 
    }

}
