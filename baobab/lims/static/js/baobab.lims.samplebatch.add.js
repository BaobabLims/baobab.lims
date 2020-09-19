function BaobabSampleBatchView() {

    var that = this;

    that.load = function () {
        // disable browser auto-complete
        $("tr[fieldname|='SamplePackage']").hide()
        $("tr[fieldname|='Strain']").hide()
        $("tr[fieldname|='Origin']").hide()
        $("tr[fieldname|='Phenotype']").hide()
        ConditionalFields()

    };


    function ConditionalFields(){
        $('#HumanOrMicroOrganism_1').click(function(event){
            $("tr[fieldname|='SamplePackage']").show()
            $("tr[fieldname|='Strain']").hide()
            $("tr[fieldname|='Origin']").hide()
            $("tr[fieldname|='Phenotype']").hide()
        });
        $('#HumanOrMicroOrganism_2').click(function(event){
            $("tr[fieldname|='SamplePackage']").hide()
            $("tr[fieldname|='Strain']").show()
            $("tr[fieldname|='Origin']").show()
            $("tr[fieldname|='Phenotype']").show()
        });
    }
}
