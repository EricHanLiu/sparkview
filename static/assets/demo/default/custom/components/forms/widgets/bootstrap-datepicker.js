var BootstrapDatepicker = function () {
    var t = function () {
        $("#m_datepicker_1, #m_datepicker_1_validate").datepicker({
            todayHighlight: !0,
            autoclose: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }).on('show.bs.modal', function(event){
           event.stopPropagation();
        }),


        $("#m_datepicker_2, #m_datepicker_2_validate").datepicker({
            todayHighlight: !0,
            autoclose: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }).on('show.bs.modal', function(event){
           event.stopPropagation();
        }),

        $("#m_datepicker_3, #m_datepicker_3_validate").datepicker({
            todayHighlight: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            autoclose: !0,
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }).on('show.bs.modal', function(event){
           event.stopPropagation();
        }),

        $("#m_datepicker_4, #m_datepicker_4_validate").datepicker({
            todayHighlight: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            autoclose: !0,
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }).on('show.bs.modal', function(event){
           event.stopPropagation();
        }),
         $("#m_datepicker_3_edit, #m_datepicker_3_edit_validate").datepicker({
            todayHighlight: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            autoclose: !0,
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }).on('show.bs.modal', function(event){
           event.stopPropagation();
        }),

        $("#m_datepicker_4_edit, #m_datepicker_4_edit_validate").datepicker({
            todayHighlight: !0,
            format: 'yyyy-mm-dd',
            orientation: "bottom left",
            autoclose: !0,
            templates: {leftArrow: '<i class="la la-angle-left"></i>', rightArrow: '<i class="la la-angle-right"></i>'}
        }).on('show.bs.modal', function(event){
           event.stopPropagation();
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