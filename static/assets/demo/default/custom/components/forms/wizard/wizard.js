//== Class definition
var WizardDemo = function () {
    //== Base elements
    var wizardEl = $('#m_wizard');
    var formEl = $('#m_form');
    var modalEl = $('#m_modal_clients');
    var validator;
    var wizard;
    var data = {};
    var gts = $('#m_gts_check');

    //== Private functions
    var initWizard = function () {
        //== Initialize form wizard
        wizard = wizardEl.mWizard({
            startStep: 1
        });

        //== Validation before going to next page
        wizard.on('beforeNext', function (wizard) {
            if (validator.form() !== true) {
                return false;  // don't go to the next step
            }

        });

        var step = wizard.getStep();

        if ( step === 1 ) {

            gts.change(function () {

                var checked = $(this).prop('checked');

                if (checked) {
                    $('#m_budget_check').attr('disabled', true);
                    $('#m_budget_label').addClass('m-checkbox--disabled');
                    $('#gts_inp').html('<input id="gts_input" name="gts_value" type="text" class="form-control m-input" placeholder="Global Target Spend">')
                }

                if(!checked) {
                    $('#m_budget_check').attr('disabled', false);
                    $('#m_budget_label').removeClass('m-checkbox--disabled');
                    $('#gts_input').remove();
                }

            });
        }


        //== Change event
        wizard.on('change', function (wizard) {
            mApp.scrollTop();
            let data = formEl.serializeArray();

            if (wizard.isLastStep()) {
                console.log(data);
                let dataObj = {};
                $(data).each(function(i, field) {
                    dataObj[field.name] = field.value
                });
                console.log(dataObj);
                $('#client_name_fstep').html(dataObj['client_name']);

                // if (budget.prop('checked')) {
                //     $('#budget_fstep').remove();
                // } else {
                //     $('#client_budget_fstep').html(dataObj['gts_value']);
                // }
                //
                // $('#aw_name_fstep').html(dataObj['adwords']);
            }
        });
    };

    var initValidation = function () {
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
                gts_value: {
                    required: true,
                    digits: true,
                    max: 10000000

                },
                aw_budget: {
                    digits: true,
                    max: 10000000

                },
                bing_budget: {
                    digits: true,
                    max: 10000000

                },
                facebook_budget: {
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
                },
                gts_value: {
                    digits: 'Only digits are allowed in this field.',
                    required: 'A global target spend for the new client is required.'
                }
            },

            //== Display error
            invalidHandler: function (event, validator) {
                mApp.scrollTop();
                toastr.error("There are some errors in your submission. Please correct them.");
            }

            //== Submit valid form
            // submitHandler: function (form) {
            // }
        });
    };

    var initSubmit = function () {
        var btn = formEl.find('[data-wizard-action="submit"]');
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        btn.on('click', function (e) {
            e.preventDefault();
            if (validator.form()) {

                formEl.ajaxSubmit({
                    type: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    data: data,
                    url: '',
                    success: function () {
                        toastr.success("New client added to the database.");
                        formEl.resetForm();
                        modalEl.modal('hide');
                        wizardEl.goFirst();
                    },
                    error: function (ajaxContext) {
                        toastr.error(ajaxContext.statusText)
                    },
                    complete: function () {
                        setTimeout(function () {
                            location.reload();
                        }, 2500);
                    }
                });
            }
        });
    };

    return {
        // public functions
        init: function () {
            wizardEl = $('#m_wizard');
            formEl = $('#m_form');
            modalEl = $('#m_modal_clients');

            initWizard();
            initValidation();
            initSubmit();
        }
    };
}();

var WizardCampaigns = function () {
    //== Base elements
    var wizardEl = $('#m_wizard_campaigns');
    var formEl = $('#m_form_campaigns');
    var modalEl = $('#m_modal_campaigns');
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
        wizard.on('beforeNext', function (wizard) {
            if (validator.form() !== true) {
                return false;  // don't go to the next step
            }

        });

        //== Change event
        wizard.on('change', function (wizard) {
            mApp.scrollTop();
            data = formEl.serialize();
            console.log(data);

            if (wizard.isLastStep()) {
                $('#client_name_fstep').html(client_name.value);
                // $('#client_budget_fstep').html(client_budget.value);
                // $('#aw_name_fstep').html(data.adwords.value);
            }
        });
    };

    var initValidation = function () {
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
                aw_budget: {
                    required: true,
                    digits: true,
                    min: 1,
                    max: 10000000

                },
                bing_budget: {
                    required: true,
                    digits: true,
                    min: 1,
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
            invalidHandler: function (event, validator) {
                mApp.scrollTop();
                toastr.error("There are some errors in your submission. Please correct them.");
            }

            //== Submit valid form
            // submitHandler: function (form) {
            // }
        });
    };

    var initSubmit = function () {
        var btn = formEl.find('[data-wizard-action="submit"]');
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        btn.on('click', function (e) {
            e.preventDefault();
            if (validator.form()) {
                //== See: http://malsup.com/jquery/form/#ajaxSubmit

                formEl.ajaxSubmit({
                    type: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    data: data,
                    url: '',
                    success: function () {
                        swal({
                            "title": "",
                            "text": "New grouping added to the database.",
                            "type": "success",
                            "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                        });
                        formEl.resetForm();
                        modalEl.modal('hide');
                        wizardEl.goFirst();
                    },
                    error: function (ajaxContext) {
                        swal({
                            "title": "",
                            "text": ajaxContext.statusText,
                            "type": "error",
                            "confirmButtonClass": "btn btn-secondary m-btn m-btn--wide"
                        });
                    },
                    complete: function () {
                        setTimeout(function () {
                            location.reload();
                        }, 2500);
                    }
                });
            }
        });
    };

    return {
        // public functions
        init: function () {
            wizardEl = $('#m_wizard_campaigns');
            formEl = $('#m_form_campaigns');
            modalEl = $('#m_modal_campaigns');

            initWizard();
            initValidation();
            initSubmit();
        }
    };
}();

jQuery(document).ready(function () {
    WizardDemo.init();
    WizardCampaigns.init();
});