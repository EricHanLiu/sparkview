//== Class definition
var WizardDemo = function () {
    //== Base elements
    var wizardEl = $('#m_wizard');
    var formEl = $('#m_form');
    var modalEl = $('#m_modal_clients');
    var validator;
    var wizard;
    var data = {};
    
    //== Private functions
    var initWizard = function () {
        //== Initialize form wizard
        wizard = wizardEl.mWizard({
            startStep: 1
        });

        //== Validation before going to next page
        wizard.on('beforeNext', function(wizard) {
            if (validator.form() !== true) {
                return false;  // don't go to the next step
            }

        });

        //== Change event
        wizard.on('change', function(wizard) {
            mApp.scrollTop();
            data = formEl.serializeArray();
        });
    };

    var initValidation = function() {
        validator = formEl.validate({
            //== Validate only visible fields
            ignore: ":hidden",

            // == Validation rules
            rules: {
                //=== Client Information(step 1)
                //== Client details
                client_name: {
                    required: true
                }
            },

            //== Validation messages
            messages: {
                name: {
                    required: 'You must enter a client name'
                }
            },

            //== Display error
            invalidHandler: function(event, validator) {
                mApp.scrollTop();

                swal({
                    "title": "",
                    "text": "There are some errors in your submission. Please correct them.",
                    "type": "error",
                    "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                });
            },

            //== Submit valid form
            // submitHandler: function (form) {
            // }
        });
    };

    var initSubmit = function() {
        var btn = formEl.find('[data-wizard-action="submit"]');
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        btn.on('click', function(e) {
            e.preventDefault();

            if (validator.form()) {
                //== See: http://malsup.com/jquery/form/#ajaxSubmit
                console.log(data);
                formEl.ajaxSubmit({
                    type: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    data: data,
                    url: '',
                    success: function() {
                        formEl.resetForm();
                        modalEl.modal('hide');

                        swal({
                            "title": "",
                            "text": "New client added to the database.",
                            "type": "success",
                            "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                        });
                        wizardEl.goFirst();
                    },
                    error: function(ajaxContext) {
                        console.log(ajaxContext);
                    }
                });
            }
        });
    };

    return {
        // public functions
        init: function() {
            wizardEl = $('#m_wizard');
            formEl = $('#m_form');
            modalEl = $('#m_modal_clients');

            initWizard(); 
            initValidation();
            initSubmit();
        }
    };
}();

jQuery(document).ready(function() {    
    WizardDemo.init();
});