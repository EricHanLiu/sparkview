var Select2 = function () {
    var e = function () {

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
        $('#m_select2_adwords').on('select2:select', function (e) {
            var data = e.params.data;
            $('#budget-fields').append('<input type="number" id="' + data.id + '"name="aw_budget_' + data.id + '" class="form-control m-input m-input--air" required placeholder="Budget for ' + data.text + ' ">');
        });
        $('#m_select2_adwords').on('select2:unselect', function (e) {
            var data = e.params.data;
            $("#" + data.id).remove();
        });
        $('#m_select2_bing').on('select2:select', function (e) {
            var data = e.params.data;
            $('#budget-fields-bing').append('<input type="number" id="' + data.id + '" name="bing_budget_' + data.id + '"  class="form-control m-input m-input--air" required placeholder="Budget for ' + data.text + '">');
        });
        $('#m_select2_bing').on('select2:unselect', function (e) {
            var data = e.params.data;
            $("#" + data.id).remove();
        });
        $("#m_select2_campaigns").select2({
            placeholder: "Search..."
        });
        // $('#m_select2_campaigns').on('select2:select', function (e) {
        //     var data = e.params.data;
        //     $('#budget-fields').append('<input type="number" id="' + data.id + '"name="cmp_budget_'+ data.id +'" class="form-control m-input m-input--air" required placeholder="Budget for ' + data.text + ' ">');
        // });
        // $('#m_select2_campaigns').on('select2:unselect', function (e) {
        //     var data = e.params.data;
        //     $("#" + data.id).remove();
        // });
    };
    return {
        init: function () {
            e()
        }
    }
}();
jQuery(document).ready(function () {
    Select2.init()
});