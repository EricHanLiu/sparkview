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
    let budget = $("#m_budget_check");

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

        if (step === 1) {

            gts.change(function () {

                var checked = $(this).prop('checked');

                if (checked) {
                    $('#m_budget_check').attr('disabled', true);
                    $('#m_budget_label').addClass('m-checkbox--disabled');
                    $('#gts_inp').html('<input id="gts_input" name="gts_value" type="text" class="form-control m-input" placeholder="Global Target Spend">')
                }

                if (!checked) {
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
            console.log(data);
            var obj = {};

            for(var i = 0; i < data.length; i++){
                obj[data[i].name] = data[i].value;
            }

            if (wizard.isLastStep()) {

                let dataObj = {};
                let aw = $('#aw_name_fstep');
                let bing = $('#bing_name_fstep');
                let fb = $('#fb_name_fstep');

                $(data).each(function (i, item) {
                    dataObj[item.name] = item.value
                });

                const acc_budgets = [[aw, "adwords"], [bing, "bing"], [fb, "facebook"]];

                for (acc_type of acc_budgets) {
                    let $acc_elm = acc_type[0];
                    let acc_name = acc_type[1];

                    $acc_elm.html($(`select[name=${acc_name}] option:selected`).map(function () {
                        let value = $(this).val();
                        value = value.split('|');
                        return '<span class="m-badge m-badge--success m-badge--wide">' + value[1] + '</span>';
                    }).get().join(' '));
                }

                $('#client_name_fstep').html(dataObj['client_name']);

                if (budget.prop('checked')) {
                    $('#budget_fstep').html('');
                } else {
                    $('#client_budget_fstep').html(
                        dataObj['gts_value']
                    );
                }
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
    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };

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
            data = formEl.serializeArray();
            let $cmp_elem = $("#campaigns_name_fstep");

            if (wizard.isLastStep()) {
                let dataObj = {};
                $(data).each(function (i, item) {
                    dataObj[item.name] = item.value
                });

                $cmp_elem.html($("select[name='campaigns'] option:selected").map(function () {
                    let value = $(this).val();
                    value = value.split('|');
                    return '<span class="m-badge m-badge--success m-badge--wide">' + value[1] + '</span>';
                }).get().join(' '));

                $('#campaigns_budget_fstep').html('<p>' + dataObj['grouping-budget'] + '</p>');
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
