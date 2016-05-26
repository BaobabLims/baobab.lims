function CustomStorageManageAddView(){
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
        selectChange();
        referencewidgetChange();
        textinputChange();
        textareaChange();
        checkboxChange();
    }

    function init(){
        bika.sanbi.state = {};
        bika.sanbi.shelvesnum = 0;
        storageTypeCustomization();
        dimensionCustomization();
        createStorage();
    }

    function setState(fieldname, value){
        if(fieldname && value !== undefined){
            bika.sanbi.state[fieldname] = value;
        }
    }

    function numberShelvesChange(element){
        var fieldname = $("#Shelves").parents('[data-fieldname]').attr('data-fieldname');
        if($(element).is(':checked')){
            var value = $("#Shelves").val();
            if(! bika.sanbi.shelvesnum){
                bika.sanbi.shelvesnum = value;
            }
            value = Math.pow(Math.ceil(Math.sqrt(parseInt(value))), 2);
            $("#Shelves").val(value);
            setState(fieldname, value);
            if($("#dimension select").val() === "Second"){
                dimensionCustomization();
            }
        }else{
            if(bika.sanbi.shelvesnum){
                $("#Shelves").val(bika.sanbi.shelvesnum);
                setState(fieldname, bika.sanbi.shelvesnum);
                console.log(bika.sanbi.state);
                bika.sanbi.shelvesnum = 0;
            }
            /*var pathname = window.location.pathname;
            var tempArray = pathname.split('/');
            var storageId = tempArray[tempArray.length-1];
            var request_data = {
                portal_type: "StorageManagement",
                catalog: "bika_setup_catalog",
                id: storageId
            }
            $.ajax({
                type: "POST",
                dataType: "json",
                url: window.portal_url + "/@@API/read",
                data: request_data,
                success: function(data) {
                    if(data.total_objects === 1 && $("#Shelves").val() !== 0){
                        $("#Shelves").val(bika.sanbi.shelvesnum);
                    }
                }
            });*/
        }
    }

    function referencewidgetChangeHandler(element, item){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var multivalued = $(element).attr("multivalued") == "1";
        if(multivalued){
            console.debug("Not yet inplemented");
        }
        var value = item.UID;
        setState(fieldname, value);
    }

    function referencewidgetChange(){
        $('div[data-fieldname] input.referencewidget')
            .on('selected', function(event, item){
                referencewidgetChangeHandler(this, item);
            });
    }

    function textinputChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).val();
        setState(fieldname, value);
    }

    function textinputChange(){
        $('div[data-fieldname] input[type="text"]')
            .not(".referencewidget")
            .on("change", function(event){
                textinputChangeHandler(this);
                if(event.target.id === "Shelves"){
                    numberShelvesChange($("#storageposition"));
                }
            });
        $('div[data-fieldname] input[type="number"]')
            .on("change", function(event){
                textinputChangeHandler(this);
            });
    }

    function textareaChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).val();
        setState(fieldname, value);
    }

    function textareaChange(){
        $('div[data-fieldname] textarea')
            .on('change', function(event){
                textareaChangeHandler(this);
            });
    }

    function selectChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).val();
        setState(fieldname, value);
    }

    function selectChange(){
        $("#storage_type select").on("change", function(e){
            storageTypeCustomization();
            selectChangeHandler(this);
        });

        $("#dimension select").on("change", function(e){
            dimensionCustomization();
            selectChangeHandler(this);
        });
    }

    function checkboxChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).prop("checked");
        setState(fieldname, value);
    }
    function checkboxChange(){
        $("#storageposition").on("change", function(e){
            checkboxChangeHandler(this);
            numberShelvesChange(this);
        });
        $("#letter-ids").on("change", function(e) {
            checkboxChangeHandler(this);
        });
    }

    function storageTypeCustomization(){
        if ($("#storage_type select").val() == "Freeze"){
            var html = "<label class='formQuestion' for='Shelves'>Shelves Number" +
                       "<span class='formHelp' id='shelves_help'>Specify the number of " +
                       "shelves for the new storage.</span>";
            $("#archetypes-fieldname-Shelves > label").replaceWith(html);
        }
        else if ($("#storage_type select").val() == "Tank"){
            var html = "<label class='formQuestion' for='Shelves'>Canisters Number" +
                       "<span class='formHelp' id='canisters_help'>Specify the number of " +
                       "canisters for the new storage.</span>";
            $("#archetypes-fieldname-Shelves > label").replaceWith(html);
        }
        else if($("#storage_type select").val() == "Other"){
            var html = "<label class='formQuestion' for='Shelves'>Children Number" +
                       "<span class='formHelp' id='childs_help'>Specify the number of " +
                       "children items for the new storage.</span>";
            $("#archetypes-fieldname-Shelves > label").replaceWith(html);
        }
    }

    function dimensionCustomization(){

        var fieldnameX = $("#xaxis_num").parents('[data-fieldname]').attr('data-fieldname');
        var fieldnameY = $("#yaxis_num").parents('[data-fieldname]').attr('data-fieldname');
        var fieldnameZ = $("#zaxis_num").parents('[data-fieldname]').attr('data-fieldname');
        switch($("#dimension select").val()){
            case "First":
                $("#xaxis_num").val(1);
                $("#yaxis_num").val(1);
                $("#zaxis_num").val(1);
                $("#yaxis_num").prop("disabled", true);
                $("#zaxis_num").prop("disabled", true);
                setState(fieldnameX, value);
                setState(fieldnameY, value);
                setState(fieldnameZ, value);
                break;
            case "Second":
                if($("#Shelves").val() && $("#storageposition").is(":checked")){
                    var value = Math.ceil(Math.sqrt(parseInt($("#Shelves").val())));
                    $("#xaxis_num").val(value);
                    $("#yaxis_num").val(value);
                }else{
                    $("#xaxis_num").val(1);
                    $("#yaxis_num").val(1);
                }
                setState(fieldnameX, value);
                setState(fieldnameY, value);
                setState(fieldnameZ, 1);
                console.log(bika.sanbi.state);
                $("#yaxis_num").prop("disabled", false);
                $("#zaxis_num").prop("disabled", true);
                break;
            case "Third":
                $("#yaxis_num").prop("disabled", false);
                $("#zaxis_num").prop("disabled", false);
                break;
        }
    }

    function createStorage(){
        $("#storagemanage_edit").submit(function(e){
            e.preventDefault();
            var requestData = {
                _authenticator: $("input[name='_authenticator']").val(),
                state: $.toJSON(bika.sanbi.state)
            };
            var path = window.location.href.split('/edit')[0] + '/storagemanage_submit';
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: requestData,
                success: function(data){
                    destination = window.location.origin + data['url'];
                    window.location.replace(destination)
                },
                error: function(xhr, status, error) {
                    console.log("HTML Page: " + xhr.responseText);
                    console.log(status);
                    console.log(error);
                }
            });
        });
    }
}