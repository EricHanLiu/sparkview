let removeInput = function (iid) {
    $("#row-" + iid).remove();
};

let spawnInput = function (iid, account_name) {
    $('#budget_container_' + iid).append('<div class="row no-gutters align-items-center" id="row-' + iid + '">' +
        '<div class="col-md-8">' +
        '<input type="number" id="' + iid + '" name="aw_budget_' + iid + '" ' +
        'class="form-control m-input m-input--air" placeholder="Budget for ' + account_name + ' ">' +
        '</div>' +
        '<div class="col-md-4">' +
        '<select class="form-control m-input" name="network_type_' + iid + '" id="network_type_' + iid + '" >' +
        '<option value="All">All</option>' +
        '<option value="Cross-network">Cross-network</option>' +
        '<option value="Search Network">Search</option>' +
        '<option value="Display Network">Display</option>' +
        '<option value="YouTube Search">Youtube Search</option>' +
        '<option value="YouTube Videos">Youtube Videos</option>' +
        '<option value="NOT_RELATED">Not related</option>' +
        '</select>' +
        '</div>' +
        //'<div class="col-md-1">' +
        //'<i class="fa fa-minus-circle" style="margin-left: 20px" onclick="removeInput(' + iid + ')"></i>' +
        //'</div>' +
        '</div>');
};

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

                    let budget_inputs = '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                        '<div class="row no-gutters align-items-center">' +
                        '<div class="col-md-6">' +
                        '<input type="number" id="' + iid[0] + '" name="aw_budget_' + iid[0] + '" ' +
                        'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                        '</div>' +
                        '<div class="col-md-4">' +
                        '<select class="form-control m-input" name="network_type_' + iid[0] + '" id="network_type_' + iid[0] + '" >' +
                        '<option value="All">All</option>' +
                        '<option value="Cross-network">Cross-network</option>' +
                        '<option value="Search Network">Search</option>' +
                        '<option value="Display Network">Display</option>' +
                        '<option value="YouTube Search">Youtube Search</option>' +
                        '<option value="YouTube Videos">Youtube Videos</option>' +
                        '<option value="NOT_RELATED">Not related</option>' +
                        '</select>' +
                        '</div>' +
                        '<div class="col-md-1">' +
                        '<i class="fa fa-plus-circle" style="margin-left: 20px" onclick="spawnInput(' + iid[0] + ',  \'' + data.text + '\')"></i>' +
                        '</div>' +
                        '<div class="col-md-1">' +
                        '<i class="fa fa-minus-circle" style="margin-left: 20px" onclick="removeInput(' + iid[0] + ')"></i>' +
                        '</div>' +
                        '</div>' +
                        '</div>';

                    $('#budget-fields').append(budget_inputs);
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