/*
 * Controller class for StorageOrder Add View
 */
function CustomStorageOrderAddView(){

    var that = this;
    this.load = function(){
        //disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
        referencewidgetChange();
        textinputChange();
        textareaChange();
        checkboxChange();
    }

    function showChildElements(){
        $('#ChildTitle').prop("disabled", false);
        $('#Characters').prop("disabled", false);
        $('#TwoDimension').prop("disabled", false);
        if($('#TwoDimension').prop('checked') == true) {
            $('#XAxis').prop("disabled", false);
        }else{
            $('#XAxis').prop("disabled", true);
        }
    }

    function hideChildElements(){
        $('#ChildTitle').prop('disabled', true);
        $('#ChildTitle').val('');
        $('#ChildTitle').trigger('change');
        $('#Characters').prop('disabled', true);
        $('#TwoDimension').prop('disabled', true);
        if($('#TwoDimension').prop('checked') == true){
            //$('#label-XAxis > span[class="fieldRequired"]').remove();
            $('#TwoDimension').prop('checked', false);
            $('#TwoDimension').trigger('change');
        }
        $('#XAxis').prop('disabled', true);
    }

    function init(){
        bikaSanbiState = {};

        if($('input#Number').val() > 0){
            showChildElements();
        }else{
            hideChildElements();
        }
        formSubmit();
    }

    function formSubmit(){
        createStorageLevel();
    }

    function createStorageLevel(){
        $('#storage_edit_form').submit(function(event){
            var requestData = {
                _authenticator: $("input[name='_authenticator']").val(),
                state: $.toJSON(bikaSanbiState)
            }
            var path = window.location.href.split('/edit')[0] + '/storageorder_submit';
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: requestData,
                success: function(data){
                    if (data['errors']) {
                        for (var error in data.errors) {
                            msg =  data.errors[error] + "<br/>";
                        }
                        window.bika.lims.portalMessage(msg);
                        window.scroll(0, 0);
                    }
                    else {
                        var destination = window.location.href.split("/")[0] + data['objURL'];
                        console.log(destination);
                        window.location.replace(destination);
                    }
                }
            });
        });
    }

    function stateSet(fieldname, value){
        if(fieldname && value !== undefined){
            bikaSanbiState[fieldname] = value;
        }
    }

    function referencewidgetChangeHandler(element, item){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var multivalued = $(element).attr("multivalued") == "1"
        if(multivalued){
            console.debug("Not yet inplemented");
        }
        var value = item.UID;
        stateSet(fieldname, value);
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
        var id = $(element).attr("id");
        if(id == "Number" && value > 0) showChildElements();
        else if(id == "Number") hideChildElements();
        stateSet(fieldname, value);
    }

    function textinputChange(){
        $('div[data-fieldname] input[type="text"]')
            .not(".referencewidget")
            .on('change', function(event){
                textinputChangeHandler(this);
            });
    }

    function textareaChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).val();
        stateSet(fieldname, value);
    }

    function textareaChange(){
        $('div[data-fieldname] textarea')
            .on('change', function(event){
                textareaChangeHandler(this);
            });
    }

    function XAxisRequired(){
        var label = "<span class='fieldRequired' title='Required'>" +
                        "\&nbsp;" + "</span>";
        $("#label-XAxis").append(label);
    }

    function checkboxChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).prop("checked");
        var id = $(element).attr("id");
        if(id == "TwoDimension" && value == true){
            $('#XAxis').prop("disabled", false);
            XAxisRequired();
        }
        else if(id == "TwoDimension" && value == false){
            $('#label-XAxis > span[class="fieldRequired"]').remove();
            $('#XAxis').val('');
            $('#XAxis').trigger('change');
            $('#XAxis').prop("disabled", true);
        }
        stateSet(fieldname, value);
    }

    function checkboxChange(){
        $('div[data-fieldname] input[type="checkbox"]')
            .on('change', function(event){
                checkboxChangeHandler(this);
            });
    }
}