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
        $('#archetypes-fieldname-ChildTitle').parent("td").show();
        $('#archetypes-fieldname-Characters').parent("td").show();
        $('#archetypes-fieldname-TwoDimension').parent("td").show();
        if($('input[type="checkbox"]#TwoDimension').prop('checked') == true) {
            $('div#archetypes-fieldname-XAxis').parent("td").show();
        }else{
            $('div#archetypes-fieldname-XAxis').parent("td").hide();
        }
    }

    function hideChildElements(){
        $('#archetypes-fieldname-ChildTitle').parent("td").hide();
        $('#archetypes-fieldname-Characters').parent("td").hide();
        $('#archetypes-fieldname-TwoDimension').parent("td").hide();
        if($('input[type="checkbox"]#TwoDimension').prop('checked') == true){
            $('#archetypes-fieldname-XAxis > label > span[class="required"]').remove();
            //$('input[type="checkbox"]#TwoDimension').attr('checked', false);
            //$('#archetypes-fieldname-XAxis').val(0);
        }
        $('#archetypes-fieldname-XAxis').parent("td").hide();
    }

    function init(){
        bikaSanbiState = {}
        console.log($('input#Number').val());
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
                    console.log(data['success']);
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
        var fieldname = $(element).parents('[fieldname]').attr('fieldname');
        var multivalued = $(element).attr("multivalued") == "1"
        if(multivalued){
            console.debug("Not yet inplemented");
        }
        var value = item.UID;
        stateSet(fieldname, value);
    }

    function referencewidgetChange(){
        $('tr[fieldname] input.referencewidget')
            .on('selected', function(event, item){
                referencewidgetChangeHandler(this, item);
            });
    }

    function textinputChangeHandler(element){
        var fieldname = $(element).parents('[fieldname]').attr('fieldname');
        var value = $(element).val();
        var id = $(element).attr("id");
        if(id == "Number" && value > 0) showChildElements();
        else if(id == "Number") hideChildElements();
        stateSet(fieldname, value);
    }

    function textinputChange(){
        $('tr[fieldname] input[type="text"]')
            .not(".referencewidget")
            .on('change', function(event){
                textinputChangeHandler(this);
            });
    }

    function textareaChangeHandler(element){
        var fieldname = $(element).parents('[fieldname]').attr('fieldname');
        var value = $(element).val();
        stateSet(fieldname, value);
    }

    function textareaChange(){
        $('tr[fieldname] textarea')
            .on('change', function(event){
                textareaChangeHandler(this);
            });
    }

    function XAxisRequired(){
        var label = "<span class='required' title='required'>" +
                        "\&nbsp;" + "</span>";
        $(label).insertBefore($('#archetypes-fieldname-XAxis > label > span'));
    }

    function checkboxChangeHandler(element){
        var fieldname = $(element).parents('[fieldname]').attr('fieldname');
        var value = $(element).prop("checked");
        var id = $(element).attr("id");
        if(id == "TwoDimension" && value == true){
            $('#archetypes-fieldname-XAxis').parent("td").show();
            XAxisRequired();
        }
        else if(id == "TwoDimension" && value == false){
            $('#archetypes-fieldname-XAxis > label > span[class="required"]').remove();
            $('#archetypes-fieldname-XAxis').parent("td").hide();
        }
        stateSet(fieldname, value);
    }

    function checkboxChange(){
        $('tr[fieldname] input[type="checkbox"]')
            .on('change', function(event){
                checkboxChangeHandler(this);
            });
    }
}