var Select2 = function () {
    var e = function () {

            let checkbox = $('#m_gts_check');

            $("#m_select2_adwords").select2({
                placeholder: "Search..."
            });

            $("#m_select2_adwords_cm2").select2({
                placeholder: "Search..."
            });

            $("#m_select2_adwords_cm3").select2({
                placeholder: "Search..."
            });

            $("#m_select2_bing").select2({
                placeholder: "Search..."
            });

            $("#m_select2_bing_cm2").select2({
                placeholder: "Search..."
            });

            $("#m_select2_bing_cm3").select2({
                placeholder: "Search..."
            });

            $("#m_select2_facebook").select2({
                placeholder: "Search..."
            });

            $("#m_select2_facebook_cm2").select2({
                placeholder: "Search..."
            });

            $("#m_select2_facebook_cm3").select2({
                placeholder: "Search..."
            });

            $('#m_select2_adwords').on('select2:select', function (e) {

                if (!checkbox.prop('checked')) {
                    let data = e.params.data;
                    let iid = data.id;
                    iid = iid.split('|');
                    $('#budget-fields').append('' +
                        '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                        // '<label class="m-checkbox m-checkbox--solid m-checkbox--danger yt" id="yt_lbl_'+ iid[0] +'">\n' +
                        // '<input type="checkbox" name="aw_yt_' + iid[0] +'" id="aw_yt_' + iid[0] +'">Youtube' +
                        // '<span></span></label>' +
                        //'<label class="m-checkbox m-checkbox--solid m-checkbox--success nl" id="aw_lbl_' + iid[0] + '">\n' +
                        //'<input type="checkbox" name="aw_nl_' + iid[0] + '" id="aw_nl_' + iid[0] + '">Not Linked' +
                        //'<span></span></label>' +
                        '<input type="number" id="' + iid[0] + '" name="aw_budget_' + iid[0] + '" ' +
                        'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                        '</div>');
                }
            });

            $('#m_select2_adwords').on('select2:unselect', function (e) {
                var data = e.params.data;
                let iid = data.id;
                iid = iid.split('|');
                $("#" + iid[0]).remove();
                $("#budget_container_" + iid[0]).remove();
            });

            $('#m_select2_bing').on('select2:select', function (e) {
                if (!checkbox.prop('checked')) {
                    var data = e.params.data;
                    let iid = data.id;
                    iid = iid.split('|');
                    $('#budget-fields-bing').append('' +
                        '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                        //'<label class="m-checkbox m-checkbox--solid m-checkbox--success" id="aw_lbl_' + iid[0] + '">\n' +
                        //'<input type="checkbox" name="bing_nl_' + iid[0] + '" id="bing_nl_' + iid[0] + '">Not Linked' +
                        //'<span></span></label>' +
                        '<input type="number" id="' + iid[0] + '" name="bing_budget_' + iid[0] + '" ' +
                        'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                        '</div>');
                }
            });

            $('#m_select2_bing').on('select2:unselect', function (e) {
                var data = e.params.data;
                let iid = data.id;
                iid = iid.split('|');
                $("#budget_container_" + iid[0]).remove();
            });

            $('#m_select2_facebook').on('select2:select', function (e) {
                    if (!checkbox.prop('checked')) {
                        var data = e.params.data;
                        let iid = data.id;
                        iid = iid.split('|');
                        $('#budget-fields-facebook').append('' +
                            '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                            //'<label class="m-checkbox m-checkbox--solid m-checkbox--success pull-right">\n' +
                            //'<input type="checkbox" name="fb_nl_' + iid[0] + '" id="fb_nl_' + iid[0] + '">Not Linked' +
                            //'<span></span></label>' +
                            '<input type="number" id="' + iid[0] + '" name="facebook_budget_' + iid[0] + '" ' +
                            'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                            '</div>');
                    }
                }
            );

            $('#m_select2_facebook').on('select2:unselect', function (e) {
                var data = e.params.data;
                let iid = data.id;
                iid = iid.split('|');
                $("#budget_container_" + iid[0]).remove();
            });
            $("#m_select2_campaigns").select2({
                placeholder: "Search..."
            });

            $("#select_adwords").select2({
                placeholder: "Search accounts..."
            });

            $("#select_labels").select2({
                placeholder: "Search labels..."
            });
// $('#m_select2_campaigns').on('select2:select', function (e) {
//     var data = e.params.data;
//     $('#budget-fields').append('<input type="number" id="' + data.id + '"name="cmp_budget_'+ data.id +'" class="form-control m-input m-input--air" required placeholder="Budget for ' + data.text + ' ">');
// });
// $('#m_select2_campaigns').on('select2:unselect', function (e) {
//     var data = e.params.data;
//     $("#" + data.id).remove();
// });
        }
    ;
    return {
        init: function () {
            e()
        }
    }
}
();
jQuery(document).ready(function () {
    Select2.init()
});