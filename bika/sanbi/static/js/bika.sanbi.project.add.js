function CustomProjectAddView(){
    var biospecFd = '#archetypes-fieldname-Biospecimens';
    var biospecSel = '#archetypes-fieldname-Biospecimens #Biospecimens';
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
        applyStyles();
        biospecimens();
    }

    function init() {
        getAnalyses();
    }

    function getAnalyses(){
        var path = window.location.href.split('/edit')[0] + '/analyses_biospecs';
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: path,
            success: function (data) {
                labanalysesCheckboxes(data, 'checked');
            },
            error: function (xhr, status, error) {
                console.log('some errors here!');
            }
        });
    }
    function applyStyles() {
        $(biospecFd)
            .css('border', '1px solid #cfcfcf')
            .css('background-color', '#efefef')
            .css('padding', '10px')
            .css('margin-bottom', '20px');
    }

    function biospecimens(){
        $(biospecSel).on('focusout', function (e) {
            var biospecimens = $(biospecSel).val();
            var requestData = {
                '_authenticator': $("input[name='_authenticator']").val(),
                'biospecs': biospecimens
            };
            var path = window.location.href.split('/edit')[0] + '/analyses_biospecs';
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: requestData,
                success: function(data){
                    labanalysesCheckboxes(data, '');
                },
                error: function(xhr, status, error){
                    console.log('some errors here!');
                }
            });
         });
    }

    function labanalysesCheckboxes(data, checked) {
        if(data.length > 0){
            var html = "<table class='analyses'>" +
                        "<thead>" +
                        "<tr>" +
                        "<th i18n:translate=''></th>" +
                        "<th i18n:translate=''>Analysis</th>" +
                        "<th i18n:translate=''>Biospecimen type</th>" +
                        "</tr></thead>" +
                        "<tbody>";

            $.each(data, function (i,v) {
                html = html + "<tr><td><input type='checkbox' name='Analyses' id='" + v['uid'] +
                       "' value='"+ v['uid'] +"'"+ checked + "/></td>";
                html = html + "<td>"+ v['title'] +"</td>";
                html = html + "<td>"+ v['bio_title'] +"</td></tr>";
            });
            var html = html + "</tbody></table>";

            $("#labanalyses-uids").html(html);
        }
    }
}