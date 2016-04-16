function CustomStorageManageAddView(){
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
        selectChange();
        referencewidgetChange();
        textinputChange();
        textareaChange();
    }

    function init(){
        bika.sanbi.state = {};
        storageTypeCustomization();
        dimensionCustomization();
        createStorage();
    }

    function setState(fieldname, value){
        if(fieldname && value !== undefined){
            bika.sanbi.state[fieldname] = value;
        }
    }

    function referencewidgetChangeHandler(element, item){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var multivalued = $(element).attr("multivalued") == "1"
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
        if ($("#dimension select").val() == "First"){
            $("#yaxis_num").val(1);
            $("#yaxis_num").val(1);
            $("#zaxis_num").val(1);
            $("#yaxis_num").prop("disabled", true);
            $("#zaxis_num").prop("disabled", true);
        }
        else if ($("#dimension select").val() == "Second"){
            $("#zaxis_num").val(1);
            $("#yaxis_num").prop("disabled", false);
            $("#zaxis_num").prop("disabled", true);
        }
        else if ($("#dimension select").val() == "Third"){
            $("#yaxis_num").prop("disabled", false);
            $("#zaxis_num").prop("disabled", false);
        }
    }

    function createStorage(){
        $("#storagemanage_edit").submit(function(e){
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
                success: function(data){}
            });
        });
    }
}