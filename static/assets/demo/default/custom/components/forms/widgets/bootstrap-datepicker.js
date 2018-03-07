var BootstrapDatepicker = function () {
    var t = function () {
        $("#m_datepicker_1, #m_datepicker_1_validate").datepicker({
            todayHighlight: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }), $("#m_datepicker_1_modal").datepicker({
            todayHighlight: !0,
            orientation: "bottom left",
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }), $("#m_datepicker_2, #m_datepicker_2_validate").datepicker({
            todayHighlight: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }), $("#m_datepicker_2_modal").datepicker({
            todayHighlight: !0,
            orientation: "bottom left",
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        })
    };
    return {
        init: function () {
            t()
        }
    }
}();
jQuery(document).ready(function () {
    BootstrapDatepicker.init()
});