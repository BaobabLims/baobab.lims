function CustomStorageInventoryAddView(){
    this.load = function(){
        // disable browser auto-complete
        $('input[type=text]').prop('autocomplete', 'off');
        init();
        selectChange();
        referencewidgetChange();
        textinputChange();
        textareaChange();
    };

    function init(){
        bika.sanbi.state = {};
        createStorage();
    }

    function setState(fieldname, value){
        if(fieldname && value !== undefined){
            bika.sanbi.state[fieldname] = value;
        }
    }

    function selectChangeHandler(element){
        var fieldname = $(element).parents('[data-fieldname]').attr('data-fieldname');
        var value = $(element).val();
        setState(fieldname, value);
    }

    function selectChange(){
        $("#Type").on("change", function(e){
            selectChangeHandler(this);
        });
        $("#Dimension").on("change", function (e) {
            var value = $(this).val();
            switch (value){
                case 'f':
                case 's':
                    $("#xaxis_num").val(1);
                    $("#yaxis_num").val(1);
                    break;
                case 'N':
                    $("#xaxis_num").val(0);
                    $("#yaxis_num").val(0);
            }
            $("#xaxis_num").trigger("change");
            $("#yaxis_num").trigger("change");
            selectChangeHandler(this);
        })
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

    function createStorage(){
        $("#storageinventory_edit").submit(function(e){
            e.preventDefault();
            var requestData = {
                _authenticator: $("input[name='_authenticator']").val(),
                state: $.toJSON(bika.sanbi.state)
            };
            var path = window.location.href.split('/edit')[0] + '/storageinventory_submit';
            console.log(path);
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: path,
                data: requestData,
                success: function(data){
                    console.log('Salam');
                },
                error: function (xhr, status, error) {
                    console.log("HTMLPage: " + xhr.responseText);
                    console.log(status);
                    console.log(error);
                }
            })
        });
    }
}