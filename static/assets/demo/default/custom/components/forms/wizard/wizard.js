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
            data = formEl.serialize();
            console.log(data);

            if(wizard.isLastStep()) {
                $('#client_name_fstep').html(client_name.value);
                $('#client_budget_fstep').html(client_budget.value);
            }
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
                    required: true,
                    minlength: 3
                },
                client_budget: {
                    required: true,
                    digits: true,
                    max: 10000000

                }
            },

            //== Validation messages
            messages: {
                client_name: {
                    required: 'Please enter a client name.',
                    minlength: jQuery.validator.format('At least {0} characters are required.')
                },
                client_budget: {
                    required: 'A budget for the new client is required.',
                    digits: 'Only digits are allowed in this field.',
                    max: 'You\'re not allowed to enter numbers bigger than 10000000.'
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
            }

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

                formEl.ajaxSubmit({
                    type: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    data: data,
                    url: '',
                    success: function() {
                        formEl.resetForm();
                        modalEl.modal('hide');
                        wizardEl.goFirst();
                        swal({
                                "title": "",
                                "text": "New client added to the database.",
                                "type": "success",
                                "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"},
                                function(){
                                   location.reload();
                                });
                    },
                    error: function(ajaxContext) {
                        swal({
                            "title": "",
                            "text": ajaxContext.statusText,
                            "type": "error",
                            "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                        });
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