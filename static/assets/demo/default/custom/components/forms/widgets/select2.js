var Select2 = function () {
    var e = function () {
        $("#m_select2_adwords").select2({
            placeholder: "Search..."
        }),
        $("#m_select2_bing").select2({
            placeholder: "Search..."
        })
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